from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}>'

# Home route
@app.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

# Add new expense
@app.route('/add', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']
    if date:
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    else:
        date = datetime.date.today()

    new_expense = Expense(description=description, amount=amount, category=category, date=date)
    db.session.add(new_expense)
    db.session.commit()
    return redirect(url_for('index'))

# Edit expense
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        date = request.form['date']
        if date:
            expense.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', expense=expense)

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('index'))