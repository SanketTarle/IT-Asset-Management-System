from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.database import db
from utils.decorators import admin_required, manager_or_admin_required
from models.location import Location

locations_bp = Blueprint('locations', __name__, url_prefix='/locations')

@locations_bp.route('/')
@login_required
def index():
    locations = Location.query.order_by(Location.name).all()
    return render_template('locations.html', locations=locations)

@locations_bp.route('/add', methods=['POST'])
@login_required
@manager_or_admin_required
def add():
    name = request.form.get('name', '').strip()
    building = request.form.get('building', '').strip()
    floor = request.form.get('floor', '').strip()
    room = request.form.get('room', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Location name is required.', 'danger')
        return redirect(url_for('locations.index'))

    location = Location(
        name=name,
        building=building,
        floor=floor,
        room=room,
        description=description
    )
    db.session.add(location)
    db.session.commit()

    flash(f'Location "{name}" added successfully.', 'success')
    return redirect(url_for('locations.index'))

@locations_bp.route('/<int:location_id>/edit', methods=['POST'])
@login_required
@manager_or_admin_required
def edit(location_id):
    location = Location.query.get_or_404(location_id)
    name = request.form.get('name', '').strip()
    building = request.form.get('building', '').strip()
    floor = request.form.get('floor', '').strip()
    room = request.form.get('room', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Location name cannot be empty.', 'danger')
        return redirect(url_for('locations.index'))

    location.name = name
    location.building = building
    location.floor = floor
    location.room = room
    location.description = description
    db.session.commit()

    flash(f'Location "{name}" updated successfully.', 'success')
    return redirect(url_for('locations.index'))

@locations_bp.route('/<int:location_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(location_id):
    location = Location.query.get_or_404(location_id)

    asset_count = location.assets.count()
    if asset_count > 0:
        flash(f'Cannot delete location "{location.name}" because {asset_count} assets are registered at this location.', 'danger')
        return redirect(url_for('locations.index'))

    name = location.name
    db.session.delete(location)
    db.session.commit()

    flash(f'Location "{name}" deleted successfully.', 'info')
    return redirect(url_for('locations.index'))

