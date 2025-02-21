from flask import Flask, render_template, request, redirect, url_for, Response
from flask_migrate import Migrate
from models import db, Contact
from dotenv import load_dotenv
import os
import csv
from faker import Faker
import qrcode
from io import BytesIO
from flask import send_file



load_dotenv()

app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


    
migrate = Migrate(app, db)

#fake = Faker()



@app.route('/')
def home():
    contacts = []

    #rechercher un contact
    search_query = request.args.get('search','')
    if search_query:
        contacts = Contact.query.filter(
            (Contact.name.ilike(f"%{search_query}%")) |
            (Contact.phone.ilike(f"%{search_query}%")) |
            (Contact.email.ilike(f"%{search_query}%"))
        ).all()
    else:
        contacts = Contact.query.all()
    return render_template('home.html', contacts=contacts, search_query=search_query)


#ajouter un contact
@app.route('/add_contact', methods=['POST', 'GET'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
    
        new_contact = Contact(name=name, email=email, phone=phone)
        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('add_contact.html')


#modifier un contact

@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = Contact.query.get(contact_id)  

    if request.method == 'POST':
        contact.name = request.form['name']  
        contact.phone = request.form['phone']  
        contact.email = request.form['email']
        
        db.session.commit()  
        return redirect(url_for('home'))  

    return render_template('edit_contact.html', contact=contact)  




#supprimer un contact
@app.route('/delete/<int:contact_id>', methods=['GET', 'POST'])
def delete_contact(contact_id):
    contact = Contact.query.get(contact_id) 

    db.session.delete(contact)  
    db.session.commit()  

    return redirect(url_for('home')) 

"""
#exporter les conctact via csv
@app.route('/export/csv')
def export_csv():
    contacts = Contact.query.all()

    def generate_csv():
        yield "Nom, Numéro de téléphone, Email\n"
        for contact in contacts:
            yield f"{contact.name},{contact.phone},{contact.email } \n"
        
    response = Response(generate_csv(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=contacts.csv"

    return response
"""
#exporter via excel
from flask import send_file
from openpyxl import Workbook
import io

@app.route('/export/excel')
def export_excel():
    # Récupérer les contacts depuis la base de données
    contacts = Contact.query.all()

    # Créer un fichier Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contacts"

    # Ajouter les en-têtes (Sans l'argument `methods`)
    sheet.append(["Nom", "Numéro de téléphone", "Email"])

    # Ajouter les données des contacts
    for contact in contacts:
        sheet.append([contact.name, contact.phone, contact.email or ""])

    # Enregistrer le fichier dans un flux mémoire
    file_stream = io.BytesIO()
    workbook.save(file_stream)
    file_stream.seek(0)

    # Retourner le fichier en tant que réponse téléchargeable
    return send_file(
        file_stream,
        as_attachment=True,
        download_name="contacts.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

#generer des données automatiquement
@app.route('/generate-fake-contact/<int:count>')
def generate_fake_contacts(count):
    for i in range(count):
        fake_contact = Contact(
            name = fake.name(),
            phone = fake.phone_number(),
            email = fake.email()
        )
        db.session.add(fake_contact)
    db.session.commit()
    return redirect(url_for('home'))


#generation d'un qrcode
@app.route('/generate_qr/<int:contact_id>')
def generate_qr(contact_id):
    # Générer l'URL de la page du contact
    contact_url = url_for('contact_details', contact_id=contact_id, _external=True)

    # Générer le QR Code
    qr = qrcode.make(contact_url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@app.route('/contact/<int:contact_id>')
def contact_details(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    return render_template('contact_detail.html', contact=contact)

    

if __name__ == '__main__':
    app.run(debug=True)