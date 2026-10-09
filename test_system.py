"""
Automated System Verification Script for Asset Management System
Executes exhaustive testing across all database tables, endpoints, and workflows.
"""

import os
import sys

# Ensure UTF-8 output if supported
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    print("=" * 70)
    print("[TEST] STARTING ASSET MANAGEMENT SYSTEM COMPREHENSIVE VERIFICATION")
    print("=" * 70)

    from app import create_app
    from utils.database import db
    from models.user import User
    from models.asset import Asset
    from models.category import Category
    from models.location import Location
    from models.employee import Employee
    from models.assignment import AssetAssignment
    from models.maintenance import MaintenanceRecord
    from models.transaction import AssetTransaction

    app = create_app()
    client = app.test_client()

    with app.app_context():
        # 1. Verify database.db exists
        db_path = os.path.join(app.root_path, 'database.db')
        assert os.path.exists(db_path), "database.db file does not exist!"
        print("[PASS] [Test 1] database.db verified in project root.")

        # 2. Verify all tables exist and have schema
        tables = db.metadata.tables.keys()
        expected_tables = [
            'users', 'categories', 'locations', 'employees',
            'assets', 'asset_assignments', 'maintenance_records', 'asset_transactions'
        ]
        for t in expected_tables:
            assert t in tables, f"Missing expected table {t}!"
        print(f"[PASS] [Test 2] All 8 required tables exist: {list(tables)}")

        # 3. Verify Default Admin Account
        admin = User.query.filter_by(email='admin@company.com').first()
        assert admin is not None, "Default admin user not found!"
        assert admin.check_password('Admin@123'), "Default admin password verification failed!"
        assert admin.role == 'Admin', "Default admin role is not 'Admin'!"
        print(f"[PASS] [Test 3] Default Admin verified (admin@company.com, role={admin.role})")

        # 4. Test Login via Test Client
        login_res = client.post('/login', data={
            'email': 'admin@company.com',
            'password': 'Admin@123'
        }, follow_redirects=True)
        assert login_res.status_code == 200
        assert b"Overview" in login_res.data or b"Dashboard" in login_res.data
        print("[PASS] [Test 4] Authentication successful for admin@company.com")

        # 5. Test Dashboard Statistics & API
        dash_res = client.get('/dashboard')
        assert dash_res.status_code == 200
        assert b"Company Asset Overview" in dash_res.data

        charts_res = client.get('/api/dashboard-charts')
        assert charts_res.status_code == 200
        charts_json = charts_res.get_json()
        assert 'categories' in charts_json
        assert 'statuses' in charts_json
        assert 'conditions' in charts_json
        assert 'values_by_category' in charts_json
        print("[PASS] [Test 5] Dashboard metrics and /api/dashboard-charts verified.")

        # 6. Test Category Management
        cat = Category.query.first()
        assert cat is not None, "Categories table is empty!"
        print(f"[PASS] [Test 6] Category verified: {cat.name}")

        # 7. Test Location Management
        loc = Location.query.first()
        assert loc is not None, "Locations table is empty!"
        print(f"[PASS] [Test 7] Location verified: {loc.name}")

        # 8. Test Employee Creation
        emp_res = client.post('/employees/add', data={
            'employee_code': 'EMP-0099',
            'name': 'Test Engineer',
            'email': 'test.engineer@company.com',
            'phone': '+1 555-0999',
            'department': 'QA Automation',
            'designation': 'QA Lead',
            'status': 'Active'
        }, follow_redirects=True)
        assert emp_res.status_code == 200
        test_emp = Employee.query.filter_by(employee_code='EMP-0099').first()
        assert test_emp is not None, "Failed to create employee!"
        print(f"[PASS] [Test 8] Employee created: {test_emp.name} ({test_emp.employee_code})")

        # 9. Test Adding an Asset
        asset_res = client.post('/assets/add', data={
            'name': 'Test Precision Workstation',
            'category_id': cat.id,
            'manufacturer': 'Dell',
            'model': 'Precision 7780',
            'serial_number': 'TEST-SN-998877',
            'purchase_date': '2026-01-15',
            'purchase_price': '2500.00',
            'current_value': '2400.00',
            'status': 'Available',
            'condition': 'Excellent',
            'description': 'High-spec workstation for testing'
        }, follow_redirects=True)
        assert asset_res.status_code == 200
        test_asset = Asset.query.filter_by(serial_number='TEST-SN-998877').first()
        assert test_asset is not None, "Failed to create asset!"
        assert test_asset.status == 'Available'
        print(f"[PASS] [Test 9] Asset added: {test_asset.name} ({test_asset.asset_code})")

        # 10. Test Editing the Asset
        edit_res = client.post(f'/assets/{test_asset.id}/edit', data={
            'name': 'Test Precision Workstation (Updated)',
            'category_id': cat.id,
            'manufacturer': 'Dell Inc.',
            'model': 'Precision 7780 Gen 2',
            'serial_number': 'TEST-SN-998877',
            'purchase_price': '2500.00',
            'current_value': '2350.00',
            'condition': 'Good',
            'description': 'Updated description'
        }, follow_redirects=True)
        assert edit_res.status_code == 200
        db.session.refresh(test_asset)
        assert test_asset.name == 'Test Precision Workstation (Updated)'
        assert test_asset.current_value == 2350.00
        print("[PASS] [Test 10] Asset edit verified.")

        # 11. Test Asset Assignment Workflow
        assign_res = client.post(f'/assets/{test_asset.id}/assign', data={
            'employee_id': test_emp.id,
            'assigned_date': '2026-10-09',
            'notes': 'Assigned for testing purposes'
        }, follow_redirects=True)
        assert assign_res.status_code == 200
        db.session.refresh(test_asset)
        assert test_asset.status == 'Assigned', f"Expected Assigned, got {test_asset.status}"
        assert test_asset.assigned_to == test_emp.id
        
        asgn_record = AssetAssignment.query.filter_by(asset_id=test_asset.id, assignment_status='Active').first()
        assert asgn_record is not None
        assert asgn_record.employee_id == test_emp.id
        print(f"[PASS] [Test 11] Asset assigned: Status is '{test_asset.status}' assigned to {test_emp.name}")

        # 12. Test Asset Return Workflow
        return_res = client.post(f'/assets/{test_asset.id}/return', data={
            'returned_date': '2026-10-09',
            'condition': 'Good',
            'notes': 'Returned successfully after testing'
        }, follow_redirects=True)
        assert return_res.status_code == 200
        db.session.refresh(test_asset)
        assert test_asset.status == 'Available', f"Expected Available, got {test_asset.status}"
        assert test_asset.assigned_to is None
        
        db.session.refresh(asgn_record)
        assert asgn_record.assignment_status == 'Returned'
        print(f"[PASS] [Test 12] Asset returned: Status is '{test_asset.status}', custody cleared.")

        # 13. Test Maintenance Workflow
        maint_res = client.post('/maintenance/add', data={
            'asset_id': test_asset.id,
            'maintenance_type': 'Routine Inspection',
            'description': 'Annual thermal test',
            'maintenance_date': '2026-10-09',
            'cost': '75.00',
            'service_provider': 'Tech Lab',
            'status': 'In Progress'
        }, follow_redirects=True)
        assert maint_res.status_code == 200
        db.session.refresh(test_asset)
        assert test_asset.status == 'Under Maintenance', f"Expected Under Maintenance, got {test_asset.status}"
        print(f"[PASS] [Test 13] Asset marked '{test_asset.status}' during maintenance.")

        # Complete the maintenance
        maint_record = MaintenanceRecord.query.filter_by(asset_id=test_asset.id).first()
        assert maint_record is not None
        complete_maint_res = client.post(f'/maintenance/{maint_record.id}/edit', data={
            'maintenance_type': maint_record.maintenance_type,
            'description': maint_record.description,
            'maintenance_date': '2026-10-09',
            'cost': '75.00',
            'service_provider': 'Tech Lab',
            'status': 'Completed'
        }, follow_redirects=True)
        assert complete_maint_res.status_code == 200
        db.session.refresh(test_asset)
        assert test_asset.status == 'Available', f"Expected Available after completion, got {test_asset.status}"
        print(f"[PASS] [Test 14] Maintenance completed: Asset restored to '{test_asset.status}'")

        # 14. Test Search and Filter
        search_res = client.get('/assets/?q=Precision')
        assert search_res.status_code == 200
        assert b"Test Precision Workstation" in search_res.data
        print("[PASS] [Test 15] Asset search query verified.")

        # 15. Test All 7 Reports and CSV Exports
        report_types = [
            'all_assets', 'assigned_assets', 'available_assets',
            'maintenance', 'retired_assets', 'asset_value', 'employee_assets'
        ]
        for r_type in report_types:
            rep_res = client.get(f'/reports/?type={r_type}')
            assert rep_res.status_code == 200, f"Failed loading report: {r_type}"
            csv_res = client.get(f'/reports/export-csv?type={r_type}')
            assert csv_res.status_code == 200, f"Failed exporting CSV for {r_type}"
            assert csv_res.headers.get('Content-Type', '').startswith('text/csv')
        print("[PASS] [Test 16] All 7 Reports and CSV export endpoints verified.")

        # 16. Test System Settings & Database Backup Endpoint
        backup_res = client.get('/settings/backup-db')
        assert backup_res.status_code == 200
        assert len(backup_res.data) > 0
        print("[PASS] [Test 17] Database live backup download verified.")

        # 17. Test Deleting the Test Asset
        del_asset_id = test_asset.id
        del_res = client.post(f'/assets/{del_asset_id}/delete', follow_redirects=True)
        assert del_res.status_code == 200
        deleted_asset = db.session.get(Asset, del_asset_id)
        assert deleted_asset is None, "Asset was not deleted!"
        print("[PASS] [Test 18] Asset deletion verified.")

        # Delete the test employee
        client.post(f'/employees/{test_emp.id}/delete', follow_redirects=True)
        deleted_emp = db.session.get(Employee, test_emp.id)
        assert deleted_emp is None, "Test employee was not deleted!"
        print("[PASS] [Test 19] Employee deletion verified.")

        # 18. Test Error Pages (404 and 500)
        res_404 = client.get('/non-existent-page-xyz')
        assert res_404.status_code == 404
        assert b"404" in res_404.data
        print("[PASS] [Test 20] Custom 404 error page verified.")

        # 19. Test Logout
        logout_res = client.get('/logout', follow_redirects=True)
        assert logout_res.status_code == 200
        assert b"Sign In" in logout_res.data or b"logged out" in logout_res.data
        print("[PASS] [Test 21] User logout verified.")

    print("=" * 70)
    print("[SUCCESS] ALL 21 TEST SUITES PASSED FLAWLESSLY WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
