# Phase 5: Update Existing Flows - COMPLETED

## What changed
- Added image upload to the Add Employee flow in `frontend/index.html`.
- When an employee is created successfully, if an image was selected in the add form, it is uploaded via `uploadEmployeeImage(emp_id, file)`.
- On success, a success message is shown; on failure, a warning message is shown. The modal closes, table reloads, and the add form image preview and input are reset.

## UX impact
- One-step create + optional image upload.
- Immediate feedback and refreshed list.
- Form resets to allow adding the next employee quickly.

## Files touched
- `frontend/index.html`: Updated `submitAddForm` to include post-create image upload and reset logic.

## How to test
1. Start backend (port 8000) and frontend (port 3000).
2. Click New Employee, fill Name and Email.
3. Optionally choose an image (PNG/JPEG/JPG ≤ 2MB).
4. Click Add Employee.
5. Verify: employee appears, image shows in Image column (if provided), modal closes, form ready for next entry.
