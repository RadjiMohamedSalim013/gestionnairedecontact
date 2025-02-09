from flask import Flask, render_template, request, redirect, url_for
from models import db, Contact
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY')
print("SQLALCHEMY_DATABASE_URI:", os.getenv('SQLALCHEMY_DATABASE_URI'))

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("Base de données :", os.getenv('SQLALCHEMY_DATABASE_URI'))


db.init_app(app)




@app.route('/')
def home():
    contacts = Contact.query.all()
    return render_template('home.html', contacts=contacts)


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
    contact = Contact.query.get(contact_id)  # Récupérer le contact via son ID

    if request.method == 'POST':
        contact.name = request.form['name']  # Modifier le nom
        contact.phone = request.form['phone']  # Modifier le téléphone
        contact.email = request.form['email']  # Modifier l'email
        
        db.session.commit()  # Sauvegarder les modifications
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil

    return render_template('edit_contact.html', contact=contact)  # Afficher le formulaire pré-rempli




#supprimer un contact

@app.route('/delete/<int:contact_id>', methods=['GET'])
def delete_contact(contact_id):
    contact = Contact.query.get(contact_id) 

    db.session.delete(contact)  
    db.session.commit()  

    return redirect(url_for('home')) 


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)