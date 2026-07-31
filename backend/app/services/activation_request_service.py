import hashlib
import os
import json
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from fastapi import UploadFile, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_request import ActivationRequest, ActivationRequestStatus
from app.models.activation_request_event import ActivationRequestEvent
from app.models.license import License, LicenseStatus
from app.models.license_artifact import LicenseArtifact
from app.repositories.activation_request import activation_request_repository
from app.repositories.activation_request_event import activation_request_event_repository
from app.repositories.license import license_repository
from app.repositories.license_artifact import license_artifact_repository

from app.services.storage_service import storage_service
from app.services.parsers.parser_registry import parser_registry

from app.core.crypto import sign_payload
from app.models.license import License
from app.models.license_artifact import LicenseArtifact


class ActivationRequestService:
    async def create_from_upload(self, db: AsyncSession, file: UploadFile) -> ActivationRequest:
        file_content = await file.read()
        sha256_hash = hashlib.sha256(file_content).hexdigest()

        # Deduplication
        existing_req = await activation_request_repository.get_by_sha256(db, sha256_hash)
        if existing_req:
            return await self.get(db, existing_req.id)

        # Parse
        parser = parser_registry.get_parser(file_content, file.filename)
        if not parser:
            raise HTTPException(status_code=400, detail="Unsupported request format")

        parsed_data = parser.parse(file_content)

        # Generate request number
        req_number = await activation_request_repository.generate_request_number(db)

        # Save file to storage
        destination_name = f"requests/{req_number}_{file.filename}"
        storage_path = await storage_service.save(file_content, destination_name, file.content_type)

        # Create ActivationRequest
        req = ActivationRequest(
            request_number=req_number,
            status=ActivationRequestStatus.PENDING.value,
            request_type=parsed_data.request_type,
            
            fingerprint=parsed_data.fingerprint,
            hostname=parsed_data.hostname,
            username=parsed_data.username,
            os=parsed_data.os,
            os_version=parsed_data.os_version,
            architecture=parsed_data.architecture,
            cpu=parsed_data.cpu,
            ram=parsed_data.ram,
            bios=parsed_data.bios,
            mac_address=parsed_data.mac_address,
            windows_sid=parsed_data.windows_sid,
            current_build=parsed_data.current_build,
            timezone=parsed_data.timezone,
            locale=parsed_data.locale,
            hardware_tokens=parsed_data.hardware_tokens,

            original_filename=file.filename,
            storage_path=storage_path,
            sha256=sha256_hash,
            size=len(file_content),
            mime_type=file.content_type,
        )
        db.add(req)
        await db.flush()

        # Add initial event
        event = ActivationRequestEvent(
            request_id=req.id,
            status_from=None,
            status_to=ActivationRequestStatus.PENDING.value,
            actor_id=None,
            notes="Request uploaded and parsed"
        )
        db.add(event)
        await db.commit()
        
        # Load relationships manually or just return (API might need events)
        return await self.get(db, req.id)

    async def add_event(self, db: AsyncSession, request_id: str, status_from: str, status_to: str, actor_id: Optional[str] = None, notes: Optional[str] = None):
        event = ActivationRequestEvent(
            request_id=request_id,
            status_from=status_from,
            status_to=status_to,
            actor_id=actor_id,
            notes=notes
        )
        db.add(event)

    async def update_status(self, db: AsyncSession, request: ActivationRequest, new_status: str, actor_id: Optional[str] = None, notes: Optional[str] = None):
        old_status = request.status
        request.status = new_status
        await self.add_event(db, request.id, old_status, new_status, actor_id, notes)
        await db.commit()
        await db.refresh(request)

    async def get(self, db: AsyncSession, id: str) -> Optional[ActivationRequest]:
        return await activation_request_repository.get_with_events(db, id)

    async def get_all(self, db: AsyncSession, limit: int = 100, skip: int = 0, device_id: Optional[str] = None) -> Tuple[List[ActivationRequest], int]:
        requests = await activation_request_repository.get_multi(db, skip=skip, limit=limit, device_id=device_id)
        total = await activation_request_repository.count(db, device_id=device_id)
        return requests, total

    async def reject(self, db: AsyncSession, id: str, reason: str, actor_id: str, notes: Optional[str] = None) -> ActivationRequest:
        req = await self.get(db, id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        req.reject_reason = reason
        if notes:
            req.admin_notes = notes
        req.rejected_by = actor_id
        req.rejected_at = datetime.now(timezone.utc)
        
        await self.update_status(db, req, ActivationRequestStatus.REJECTED.value, actor_id, f"Rejected: {reason}")
        return req

    async def review(self, db: AsyncSession, id: str, actor_id: str) -> ActivationRequest:
        req = await self.get(db, id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
            
        if req.status != ActivationRequestStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Only pending requests can be reviewed")
            
        await self.update_status(db, req, ActivationRequestStatus.UNDER_REVIEW.value, actor_id, "Review started")
        return req

    async def generate_license(self, db: AsyncSession, id: str, config: dict, actor_id: str) -> ActivationRequest:
        req = await self.get(db, id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        if req.status not in [ActivationRequestStatus.UNDER_REVIEW.value, ActivationRequestStatus.APPROVED.value]:
            raise HTTPException(status_code=400, detail="Request must be under review or approved")
        
        # 1. Update status to APPROVED before generation
        await self.update_status(db, req, ActivationRequestStatus.APPROVED.value, actor_id, "Approved for generation")
        
        # 2. Build Payload
        license_id = str(uuid.uuid4())
        valid_until = None
        if config.get("validity_months"):
            valid_until = (datetime.now(timezone.utc) + timedelta(days=30 * int(config["validity_months"]))).isoformat()
            
        payload = {
            "license_id": license_id,
            "license_type": config.get("license_type", "TRIAL"),
            "issued_to": config["organization_id"],
            "machine_fingerprint": req.fingerprint,
            "issue_date": datetime.now(timezone.utc).isoformat(),
            "expiry_date": valid_until or "9999-12-31T23:59:59+00:00",
            "grace_period_days": 3,
            "features": ["ADB_ACQUISITION", "CRYPT15_DECRYPTION", "TIMELINE_EXPLORER", "MEDIA_GALLERY", "PDF_REPORTING", "OCR_TEXT_EXTRACTION", "AI_SEMANTIC_SEARCH", "CASE_COLLABORATION"],
            "tokens": req.hardware_tokens if req.hardware_tokens is not None else {}
        }
        
        # 3. Canonicalize and Sign
        canonical_json, signature_b64 = sign_payload(payload)
        
        # WFA expects a flat dictionary where the signature is alongside the payload fields
        wfalic_data = json.loads(canonical_json.decode('utf-8'))
        wfalic_data["signature"] = signature_b64
        
        wfalic_content = json.dumps(wfalic_data, indent=2).encode('utf-8')
        
        # 4. Save Artifact
        license_filename = f"{req.request_number.replace('REQ', 'LIC')}.wfalic"
        dest_name = f"licenses/{license_filename}"
        storage_path = await storage_service.save(wfalic_content, dest_name, "application/json")
        
        # 5. Create DB Records
        db_license = License(
            id=license_id,
            organization_id=config["organization_id"],
            product_id=config["product_id"],
            product_plan_id=config.get("plan_id"),
            subscription_id=None,
            deployment_id=None,
            status=LicenseStatus.ACTIVE.value,
            payload_json=payload,
            device_id=req.device_id
        )
        if valid_until:
            db_license.expires_at = datetime.fromisoformat(valid_until)
            
        db.add(db_license)
        await db.flush()
        
        artifact = LicenseArtifact(
            license_id=license_id,
            filename=license_filename,
            storage_path=storage_path,
            sha256=hashlib.sha256(wfalic_content).hexdigest(),
            size=len(wfalic_content),
            mime_type="application/json"
        )
        db.add(artifact)
        
        req.generated_license_id = license_id
        
        # 6. Update Status
        await self.update_status(db, req, ActivationRequestStatus.LICENSE_GENERATED.value, actor_id, "License generated")
        
        return req

activation_request_service = ActivationRequestService()
