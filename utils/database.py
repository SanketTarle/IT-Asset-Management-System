import os
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    Automatically creates database.db and all tables if they don't exist,
    creates the default Admin user, and seeds essential initial data
    if tables are empty.
    """
    from models.user import User
    from models.category import Category
    from models.location import Location
    from models.employee import Employee
    from models.asset import Asset
    from models.assignment import AssetAssignment
    from models.maintenance import MaintenanceRecord
    from models.transaction import AssetTransaction

    with app.app_context():
        # Ensure upload directories exist
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

        # Create all tables in SQLite database.db
        db.create_all()

        # 1. Check & Seed Default Administrator Account
        admin = User.query.filter_by(email='admin@company.com').first()
        if not admin:
            admin = User(
                name='System Administrator',
                email='admin@company.com',
                role='Admin'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("[AMS] Default Administrator created (admin@company.com / Admin@123)")

        # Also create a demo Manager and Employee account if not existing for role testing
        manager = User.query.filter_by(email='manager@company.com').first()
        if not manager:
            manager = User(
                name='Operations Manager',
                email='manager@company.com',
                role='Manager'
            )
            manager.set_password('Manager@123')
            db.session.add(manager)

        emp_user = User.query.filter_by(email='sarah.jenkins@company.com').first()
        if not emp_user:
            emp_user = User(
                name='Sarah Jenkins',
                email='sarah.jenkins@company.com',
                role='Employee'
            )
            emp_user.set_password('Employee@123')
            db.session.add(emp_user)
        db.session.commit()

        # 2. Seed Default Categories if none exist
        if Category.query.count() == 0:
            default_categories = [
                Category(name='Laptops & Computers', description='Workstations, high-performance laptops, ultrabooks and desktops'),
                Category(name='Monitors & Displays', description='4K monitors, dual screens, conference room displays and projectors'),
                Category(name='Mobile Devices & Tablets', description='Smartphones, iPads, tablets and testing devices'),
                Category(name='Office Equipment & Printers', description='Printers, scanners, shredders, telephony and conference units'),
                Category(name='Furniture & Fixtures', description='Ergonomic desks, executive chairs, storage cabinets and lounge units'),
                Category(name='Network & Infrastructure', description='Routers, switches, rack servers, patch panels and UPS units'),
                Category(name='Software Licenses', description='Enterprise software subscriptions, cloud suites and developer licenses'),
                Category(name='Vehicles & Transport', description='Company fleet vehicles, utility vans and service delivery cars'),
            ]
            db.session.add_all(default_categories)
            db.session.commit()
            print("[AMS] Initial Categories seeded successfully.")

        # 3. Seed Default Locations if none exist
        if Location.query.count() == 0:
            default_locations = [
                Location(name='Headquarters - Executive Floor', building='Tower A', floor='4th Floor', room='Suite 401', description='Executive management and boardroom facilities'),
                Location(name='Engineering & IT Hub', building='Innovation Annex', floor='2nd Floor', room='Room 210', description='Software development and IT infrastructure'),
                Location(name='Finance & Operations Wing', building='Tower A', floor='3rd Floor', room='Room 305', description='Accounting, legal, HR and administrative departments'),
                Location(name='Central Inventory Warehouse', building='Logistics Center', floor='Ground Floor', room='Bay 3', description='Central storage, spare parts and incoming equipment'),
                Location(name='Design & Creative Studio', building='Innovation Annex', floor='1st Floor', room='Studio B', description='UI/UX research, multimedia and creative production lab')
            ]
            db.session.add_all(default_locations)
            db.session.commit()
            print("[AMS] Initial Locations seeded successfully.")

        # 4. Seed Default Employees if none exist
        if Employee.query.count() == 0:
            loc_eng = Location.query.filter_by(name='Engineering & IT Hub').first()
            loc_des = Location.query.filter_by(name='Design & Creative Studio').first()
            loc_fin = Location.query.filter_by(name='Finance & Operations Wing').first()

            default_employees = [
                Employee(
                    employee_code='EMP-0001',
                    name='Sarah Jenkins',
                    email='sarah.jenkins@company.com',
                    phone='+1 555-0142',
                    department='Engineering',
                    designation='Senior Full-Stack Engineer',
                    location_id=loc_eng.id if loc_eng else None,
                    status='Active'
                ),
                Employee(
                    employee_code='EMP-0002',
                    name='David Miller',
                    email='david.miller@company.com',
                    phone='+1 555-0188',
                    department='Product & Design',
                    designation='Lead UI/UX Designer',
                    location_id=loc_des.id if loc_des else None,
                    status='Active'
                ),
                Employee(
                    employee_code='EMP-0003',
                    name='Emily Zhang',
                    email='emily.zhang@company.com',
                    phone='+1 555-0199',
                    department='Operations',
                    designation='Operations Director',
                    location_id=loc_fin.id if loc_fin else None,
                    status='Active'
                ),
                Employee(
                    employee_code='EMP-0004',
                    name='Michael Scott',
                    email='michael.scott@company.com',
                    phone='+1 555-0112',
                    department='Management',
                    designation='Regional Director',
                    location_id=loc_fin.id if loc_fin else None,
                    status='Active'
                )
            ]
            db.session.add_all(default_employees)
            db.session.commit()
            print("[AMS] Initial Employees seeded successfully.")

        # 5. Seed Default Assets if none exist
        if Asset.query.count() == 0:
            cat_laptop = Category.query.filter_by(name='Laptops & Computers').first()
            cat_monitor = Category.query.filter_by(name='Monitors & Displays').first()
            cat_mobile = Category.query.filter_by(name='Mobile Devices & Tablets').first()
            cat_furniture = Category.query.filter_by(name='Furniture & Fixtures').first()
            cat_network = Category.query.filter_by(name='Network & Infrastructure').first()

            loc_eng = Location.query.filter_by(name='Engineering & IT Hub').first()
            loc_des = Location.query.filter_by(name='Design & Creative Studio').first()
            loc_wh = Location.query.filter_by(name='Central Inventory Warehouse').first()

            emp_sarah = Employee.query.filter_by(employee_code='EMP-0001').first()
            emp_david = Employee.query.filter_by(employee_code='EMP-0002').first()

            today = date.today()

            # Asset 1: MacBook Pro (Assigned to Sarah)
            asset1 = Asset(
                asset_code='AST-00001',
                name='MacBook Pro 16" M3 Max',
                category_id=cat_laptop.id if cat_laptop else 1,
                description='High-performance engineering laptop with 64GB RAM and 1TB SSD',
                manufacturer='Apple Inc.',
                model='MacBook Pro 16" (2024)',
                serial_number='C02G901ABC12',
                purchase_date=today - timedelta(days=120),
                purchase_price=3499.00,
                current_value=3150.00,
                warranty_expiry=today + timedelta(days=610),
                supplier='Apple Enterprise Direct',
                location_id=loc_eng.id if loc_eng else 1,
                status='Assigned',
                condition='Excellent',
                assigned_to=emp_sarah.id if emp_sarah else None,
                notes='Standard issue for Lead Engineer'
            )

            # Asset 2: Dell UltraSharp 32" 4K Monitor (Assigned to David)
            asset2 = Asset(
                asset_code='AST-00002',
                name='Dell UltraSharp 32" 4K USB-C Monitor',
                category_id=cat_monitor.id if cat_monitor else 1,
                description='Color-calibrated PremierColor display with 90W USB-C hub',
                manufacturer='Dell Technologies',
                model='U3223QE',
                serial_number='CN0YF654741',
                purchase_date=today - timedelta(days=200),
                purchase_price=899.00,
                current_value=750.00,
                warranty_expiry=today + timedelta(days=530),
                supplier='CDW Corporation',
                location_id=loc_des.id if loc_des else 1,
                status='Assigned',
                condition='Excellent',
                assigned_to=emp_david.id if emp_david else None,
                notes='Assigned to Design workstation'
            )

            # Asset 3: ThinkPad P1 Gen 6 (Available in Warehouse)
            asset3 = Asset(
                asset_code='AST-00003',
                name='Lenovo ThinkPad P1 Gen 6 Workstation',
                category_id=cat_laptop.id if cat_laptop else 1,
                description='Mobile workstation with Intel Core i9, 32GB RAM, NVIDIA RTX 4080',
                manufacturer='Lenovo',
                model='ThinkPad P1 Gen 6',
                serial_number='PF3099X87',
                purchase_date=today - timedelta(days=45),
                purchase_price=2750.00,
                current_value=2600.00,
                warranty_expiry=today + timedelta(days=685),
                supplier='Lenovo Commercial',
                location_id=loc_wh.id if loc_wh else 1,
                status='Available',
                condition='Excellent',
                assigned_to=None,
                notes='Spare developer workstation ready for onboarding'
            )

            # Asset 4: iPad Pro 12.9" (Under Maintenance)
            asset4 = Asset(
                asset_code='AST-00004',
                name='Apple iPad Pro 12.9" Wi-Fi 256GB',
                category_id=cat_mobile.id if cat_mobile else 1,
                description='Retina XDR display tablet with Apple Pencil 2 for design review',
                manufacturer='Apple Inc.',
                model='iPad Pro 6th Gen',
                serial_number='DMPZ8003N98',
                purchase_date=today - timedelta(days=360),
                purchase_price=1199.00,
                current_value=850.00,
                warranty_expiry=today + timedelta(days=5),
                supplier='Apple Store for Business',
                location_id=loc_wh.id if loc_wh else 1,
                status='Under Maintenance',
                condition='Fair',
                assigned_to=None,
                notes='Battery diagnostic and port connector inspection required'
            )

            # Asset 5: Herman Miller Aeron Chair (Available)
            asset5 = Asset(
                asset_code='AST-00005',
                name='Herman Miller Aeron Ergonomic Chair',
                category_id=cat_furniture.id if cat_furniture else 1,
                description='Fully adjustable Size B graphite ergonomic task chair',
                manufacturer='Herman Miller',
                model='Aeron Chair B-Graphite',
                serial_number='HM-AER-99120',
                purchase_date=today - timedelta(days=500),
                purchase_price=1450.00,
                current_value=1200.00,
                warranty_expiry=today + timedelta(days=3150),
                supplier='Design Within Reach Enterprise',
                location_id=loc_eng.id if loc_eng else 1,
                status='Available',
                condition='Good',
                assigned_to=None,
                notes='Executive ergonomics asset'
            )

            # Asset 6: Cisco Catalyst 9300 Switch (Available)
            asset6 = Asset(
                asset_code='AST-00006',
                name='Cisco Catalyst 9300 48-Port PoE+ Switch',
                category_id=cat_network.id if cat_network else 1,
                description='Core network switch with 48 gigabit PoE+ ports and network module',
                manufacturer='Cisco Systems',
                model='C9300-48P-A',
                serial_number='FCW22190A9Z',
                purchase_date=today - timedelta(days=600),
                purchase_price=4800.00,
                current_value=3900.00,
                warranty_expiry=today + timedelta(days=495),
                supplier='Insight Enterprises',
                location_id=loc_wh.id if loc_wh else 1,
                status='Available',
                condition='Good',
                assigned_to=None,
                notes='Datacenter rack mount switch'
            )

            db.session.add_all([asset1, asset2, asset3, asset4, asset5, asset6])
            db.session.commit()

            # Create assignment history for asset1 and asset2
            if emp_sarah:
                asgn1 = AssetAssignment(
                    asset_id=asset1.id,
                    employee_id=emp_sarah.id,
                    assigned_date=today - timedelta(days=110),
                    assignment_status='Active',
                    notes='Issued during developer setup'
                )
                db.session.add(asgn1)

            if emp_david:
                asgn2 = AssetAssignment(
                    asset_id=asset2.id,
                    employee_id=emp_david.id,
                    assigned_date=today - timedelta(days=190),
                    assignment_status='Active',
                    notes='Studio 4K workstation monitor assignment'
                )
                db.session.add(asgn2)

            # Maintenance record for asset 4
            maint1 = MaintenanceRecord(
                asset_id=asset4.id,
                maintenance_type='Repair',
                description='Charging port diagnostic and screen calibration',
                maintenance_date=today - timedelta(days=2),
                cost=120.00,
                service_provider='Apple Authorized Service Provider',
                next_service_date=today + timedelta(days=180),
                status='In Progress'
            )
            db.session.add(maint1)

            # Transaction records
            for a in [asset1, asset2, asset3, asset4, asset5, asset6]:
                tx = AssetTransaction(
                    asset_id=a.id,
                    transaction_type='Registration',
                    old_value='Unregistered',
                    new_value=a.status,
                    performed_by='admin@company.com',
                    transaction_date=datetime.utcnow() - timedelta(days=30),
                    notes=f"Initial system onboarding of {a.name} ({a.asset_code})"
                )
                db.session.add(tx)

            if emp_sarah:
                tx_asgn = AssetTransaction(
                    asset_id=asset1.id,
                    transaction_type='Assignment',
                    old_value='Available',
                    new_value=f'Assigned to {emp_sarah.name}',
                    performed_by='admin@company.com',
                    transaction_date=datetime.utcnow() - timedelta(days=110),
                    notes='Asset assigned to developer'
                )
                db.session.add(tx_asgn)

            db.session.commit()
            print("[AMS] Initial Sample Assets, Assignments, and Records seeded successfully.")

