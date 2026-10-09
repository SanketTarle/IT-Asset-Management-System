from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.database import db
from utils.decorators import admin_required, manager_or_admin_required
from models.category import Category
from models.asset import Asset

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/')
@login_required
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)

@categories_bp.route('/add', methods=['POST'])
@login_required
@manager_or_admin_required
def add():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('categories.index'))

    existing = Category.query.filter_by(name=name).first()
    if existing:
        flash(f'Category "{name}" already exists.', 'danger')
        return redirect(url_for('categories.index'))

    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()

    flash(f'Category "{name}" added successfully.', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<int:category_id>/edit', methods=['POST'])
@login_required
@manager_or_admin_required
def edit(category_id):
    category = Category.query.get_or_404(category_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Category name cannot be empty.', 'danger')
        return redirect(url_for('categories.index'))

    if name != category.name:
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash(f'Category "{name}" already exists.', 'danger')
            return redirect(url_for('categories.index'))

    category.name = name
    category.description = description
    db.session.commit()

    flash(f'Category "{name}" updated successfully.', 'success')
    return redirect(url_for('categories.index'))

@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(category_id):
    category = Category.query.get_or_404(category_id)
    
    asset_count = category.assets.count()
    if asset_count > 0:
        flash(f'Cannot delete category "{category.name}" because it contains {asset_count} assets. Reassign or delete those assets first.', 'danger')
        return redirect(url_for('categories.index'))

    name = category.name
    db.session.delete(category)
    db.session.commit()

    flash(f'Category "{name}" deleted successfully.', 'info')
    return redirect(url_for('categories.index'))

