
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.appointment import Appointment
from app.models.user import User

async def check():
    async with AsyncSessionLocal() as db:
        appt_id = '48d5b490-28d8-4182-a9b3-1c9ca7f3c821'
        print(f"Checking appointment ID: {appt_id}")
        
        # Get appointment
        appt = await db.get(Appointment, appt_id)
        if not appt:
            print("APPOINTMENT NOT FOUND")
            return
        
        print(f"Found Appointment: Status={appt.status}, PatientID={appt.patient_id}")
        
        # Get patient
        patient = await db.get(User, appt.patient_id)
        if patient:
            print(f"Patient Name: {patient.full_name}")
        else:
            print("PATIENT RECORD NOT FOUND")

if __name__ == "__main__":
    asyncio.run(check())
