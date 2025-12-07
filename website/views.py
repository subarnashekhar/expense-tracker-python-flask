from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask import Flask
from flask_login import login_required, current_user
from .models import IncomeExpenses
from . import db
import json

views = Blueprint('views', __name__)

app = Flask(__name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
        entries = IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
        return render_template("home.html", user=current_user, entries = entries)


@views.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = request.form.get('amount')
        type = request.form.get('type')
        category = request.form.get('category')

        if amount == '':
            flash('Please enter a valid amount', category='error')
        elif type == '':
            flash('Please enter a valid type', category='error')
        elif category == '':
            flash('Please enter a valid category', category='error')
        else:
            entry = IncomeExpenses(amount=amount, type=type, category=category)
            db.session.add(entry)
            db.session.commit()
            flash('Income expenses added successfully')
            return redirect(url_for('views.home'))

    return render_template("add.html", user=current_user)

@views.route('/delete-post/<int:entry_id>')
@login_required
def delete(entry_id):
    entry = IncomeExpenses.query.get_or_404(int(entry_id))
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted", "success")
    return redirect(url_for('views.home'), user=current_user)



@views.route('/dashboard')
@login_required
def dashboard():
    income_vs_expense = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.type).group_by(IncomeExpenses.type).order_by(IncomeExpenses.type).all()

    category_comparison = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.category).group_by(IncomeExpenses.category).order_by(IncomeExpenses.category).all()

    dates = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.date).group_by(IncomeExpenses.date).order_by(IncomeExpenses.date).all()


    income_category = []
    for amounts, _ in category_comparison:
        income_category.append(amounts)

    income_expense = []
    for total_amount, _ in income_vs_expense:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)

    return render_template('dashboard.html',
                            income_vs_expense=json.dumps(income_expense),
                            income_category=json.dumps(income_category),
                            over_time_expenditure=json.dumps(over_time_expenditure),
                            dates_label =json.dumps(dates_label),
                            user = current_user
                        )

