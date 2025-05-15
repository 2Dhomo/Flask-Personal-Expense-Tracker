from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import io
import csv
from io import StringIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200))

@app.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        description = request.form['description']
        new_expense = Expense(amount=amount, category=category, date=date, description=description)
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/')
    return render_template('add_expense.html')

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/')

@app.route('/export')
def export_csv():
    expenses = Expense.query.all()
    data = [{
        'Amount': e.amount,
        'Category': e.category,
        'Date': e.date.strftime('%Y-%m-%d'),
        'Description': e.description
    } for e in expenses]
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='expenses.csv'
    )

@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            stream = StringIO(file.stream.read().decode('UTF-8'))
            csv_input = csv.reader(stream)
            next(csv_input)  # skip header
            for row in csv_input:
                date = datetime.strptime(row[0], '%Y-%m-%d')
                category = row[1]
                amount = float(row[2])
                description = row[3]
                expense = Expense(date=date, category=category, amount=amount, description=description)
                db.session.add(expense)
            db.session.commit()
            return redirect(url_for('index'))
    return '''
        <h2>Import Expenses from CSV</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".csv" required>
            <button type="submit">Upload</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
