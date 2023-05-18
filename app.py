from flask import Flask, request, session, redirect, url_for, render_template, flash, Response
import psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
 
app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'
 
DB_HOST = "dpg-chdon2e7avj0djj2jd8g-a.frankfurt-postgres.render.com"
DB_NAME = "infeco_db"
DB_USER = "infeco_1"
DB_PASS = "98lbxGgEybkXAaIMS6ggNKB45N7LQsE3"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
#LOGIN AND REGISTRATION 
 
 
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
    
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('login/login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('login/register.html')
   
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#LOCATAIRE

@app.route('/Locataire')
def Locataire():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    l = "SELECT * FROM locataire"
    cur.execute(l) # Execute the SQL
    list_locataire = cur.fetchall()
    return render_template('locataire/locataire.html', list_locataire = list_locataire)
 
@app.route('/add_locataire', methods=['POST'])
def add_locataire():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
        cur.execute("INSERT INTO locataire (nom_locataire, prenom_locataire) VALUES (%s,%s)", (nom_locataire, prenom_locataire))
        conn.commit()
        flash('Le locataire a bien été ajouté !')
        return redirect(url_for('Locataire'))
 
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_locataire(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM locataire WHERE locataire_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('locataire/edit_locataire.html', locataire = data[0])
 
@app.route('/update/<id>', methods=['POST'])
def update_locataire(id):
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE locataire
            SET nom_locataire = %s,
                prenom_locataire = %s,
            WHERE locataire_id = %s
        """, (nom_locataire, prenom_locataire, id))
        flash('Le locataire a bien été modifié !')
        conn.commit()
        return redirect(url_for('Locataire'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_locataire(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM locataire WHERE locataire_id = {0}'.format(id))
    conn.commit()
    flash('Le locataire a bien été supprimé !')
    return redirect(url_for('Locataire'))
 
#APPARTEMENT

@app.route('/Appartement')
def Appartement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    a = "SELECT * FROM appartement"
    cur.execute(a) # Execute the SQL
    list_appartement = cur.fetchall()
    return render_template('appartement/appartement.html', list_appartement = list_appartement)
 
@app.route('/add_appartement', methods=['POST'])
def add_appartement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_appartement = request.form['nom_appartement']
        adresse_appartement = request.form['adresse_appartement']
        complement_appartement = request.form['complement_appartement']
        ville_appartement = request.form['ville_appartement']
        codepostal_appartement = request.form['codepostal_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        depot_appartement = request.form['depot_appartement']
        cur.execute("INSERT INTO appartement (nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement, charges_appartement,loyer_appartement,depot_appartement) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement, charges_appartement,loyer_appartement,depot_appartement))
        conn.commit()
        flash('Appartement bien ajouté !')
        return redirect(url_for('Appartement'))
 
@app.route('/edit_appartement/<id>', methods = ['POST', 'GET'])
def get_appartement(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM appartement WHERE appartement_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('appartement/edit_appartement.html', appartement = data[0])
 
@app.route('/update_appartement/<id>', methods=['POST'])
def update_appartement(id):
    if request.method == 'POST':
        nom_appartement = request.form['nom_appartement']
        adresse_appartement = request.form['adresse_appartement']
        complement_appartement = request.form['complement_appartement']
        ville_appartement = request.form['ville_appartement']
        codepostal_appartement = request.form['codepostal_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        depot_appartement = request.form['depot_appartement']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE appartement
            SET nom_appartement = %s,
                adresse_appartement = %s,
                complement_appartement = %s,
                ville_appartement = %s,
                codepostal_appartement = %s,
                charges_appartement = %s,
                loyer_appartement = %s,
                depot_appartement = %s
            WHERE appartement_id = %s
        """, (nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement, charges_appartement,loyer_appartement,depot_appartement, id))
        flash('Appartement a bien été modifié !')
        conn.commit()
        return redirect(url_for('Appartement'))
 
@app.route('/delete_appartement/<string:id>', methods = ['POST','GET'])
def delete_appartement(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM appartement WHERE appartement_id = {0}'.format(id))
    conn.commit()
    flash('Appartement a bien été supprimé !')
    return redirect(url_for('Appartement'))

#AGENCE

@app.route('/Agence')
def Agence():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    a = "SELECT * FROM agence"
    cur.execute(a) # Execute the SQL
    list_agence = cur.fetchall()
    return render_template('agence/agence.html', list_agence = list_agence)
 
@app.route('/add_agence', methods=['POST'])
def add_agence():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_agence = request.form['nom_agence']
        adresse_agence = request.form['adresse_agence']
        complement_agence = request.form['complement_agence']
        ville_agence = request.form['ville_agence']
        codepostal_agence = request.form['codepostal_agence']
        frais_agence = request.form['frais_agence']
        cur.execute("INSERT INTO agence (nom_agence, adresse_agence, complement_agence, ville_agence, codepostal_agence, frais_agence) VALUES (%s,%s,%s,%s,%s,%s)", (nom_agence, adresse_agence, complement_agence, ville_agence, codepostal_agence, frais_agence))
        conn.commit()
        flash('L`agence a bien été ajouté !')
        return redirect(url_for('Agence'))
 
@app.route('/edit_agence/<id>', methods = ['POST', 'GET'])
def get_agence(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM agence WHERE agence_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('agence/edit_agence.html', agence = data[0])
 
@app.route('/update_agence/<id>', methods=['POST'])
def update_agence(id):
    if request.method == 'POST':
        nom_agence = request.form['nom_agence']
        adresse_agence = request.form['adresse_agence']
        complement_agence = request.form['complement_agence']
        ville_agence = request.form['ville_agence']
        codepostal_agence = request.form['codepostal_agence']
        frais_agence = request.form['frais_agence']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE agence
            SET nom_agence = %s,
                adresse_agence = %s,
                complement_agence = %s,
                ville_agence = %s,
                codepostal_agence = %s,
                frais_agence = %s
            WHERE agence_id = %s
        """, (nom_agence,adresse_agence, complement_agence, ville_agence, codepostal_agence, frais_agence, id))
        flash('L`agence a bien été modifié !')
        conn.commit()
        return redirect(url_for('Agence'))
 
@app.route('/delete_agence/<string:id>', methods = ['POST','GET'])
def delete_agence(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM agence WHERE agence_id = {0}'.format(id))
    conn.commit()
    flash('L`agence a bien été supprimé !')
    return redirect(url_for('Agence'))

#PAIEMENT

@app.route('/Paiement')
def Paiement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    p = "SELECT * FROM paiement"
    cur.execute(p) # Execute the SQL
    list_paiement = cur.fetchall()
    return render_template('paiement/paiement.html', list_paiement = list_paiement)
 
@app.route('/add_paiement', methods=['POST'])
def add_paiement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_paiement = request.form['nom_paiement']
        prenom_paiement = request.form['prenom_paiement']
        mois_paiement = request.form['mois_paiement']
        loyer_paiement = request.form['loyer_paiement']
        cur.execute("INSERT INTO paiement (nom_paiement, prenom_paiement, mois_paiement, loyer_paiement) VALUES (%s,%s,%s,%s)", (nom_paiement, prenom_paiement, mois_paiement, loyer_paiement))
        conn.commit()
        flash('Le paiement a bien été ajouté !')
        return redirect(url_for('Paiement'))
 
@app.route('/edit_paiement/<id>', methods = ['POST', 'GET'])
def get_paiement(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM paiement WHERE paiement_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('paiement/edit_paiement.html', paiement = data[0])
 
@app.route('/update_paiement/<id>', methods=['POST'])
def update_paiement(id):
    if request.method == 'POST':
        nom_paiement = request.form['nom_paiement']
        prenom_paiement = request.form['prenom_paiement']
        mois_paiement = request.form['mois_paiement']
        loyer_paiement = request.form['loyer_paiement']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE paiement
            SET nom_paiement = %s,
                prenom_paiement = %s,
                mois_paiement = %s,
                loyer_paiement = %s
            WHERE paiment_id = %s
        """, (nom_paiement, prenom_paiement, mois_paiement, loyer_paiement, id))
        flash('Le paiement a bien été modifié !')
        conn.commit()
        return redirect(url_for('Paiement'))
 
@app.route('/delete_paiement/<string:id>', methods = ['POST','GET'])
def delete_paiement(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM paiement WHERE paiment_id = {0}'.format(id))
    conn.commit()
    flash('Le paiement a bien été supprimé !')
    return redirect(url_for('Paiement'))

#ADMIN 


@app.route('/Admin')
def Admin():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    la = "SELECT * FROM affectation"
    cur.execute(la) # Execute the SQL
    list_des_affectations = cur.fetchall()
    return render_template('admin/admin.html', list_des_affectations = list_des_affectations)

@app.route('/affectation', methods=['POST'])
def affectation():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
        nom_appartement = request.form['nom_appartement']
        adresse_appartement = request.form['adresse_appartement']
        complement_appartement = request.form['complement_appartement']
        ville_appartement = request.form['ville_appartement']
        codepostal_appartement = request.form['codepostal_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        depot_appartement = request.form['depot_appartement']
        datee_appartement = request.form['datee_appartement']
        edl_appartement = request.form['edl_appartement']
        cur.execute("INSERT INTO affectation (nom_locataire, prenom_locataire, nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement, charges_appartement, loyer_appartement, depot_appartement,datee_appartement,edl_appartement) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (nom_locataire, prenom_locataire, nom_appartement, adresse_appartement,complement_appartement, ville_appartement, codepostal_appartement, charges_appartement, loyer_appartement, depot_appartement,datee_appartement,edl_appartement))
        conn.commit()
        flash('Le locataire a bien été ajouté !')
        return redirect(url_for('Admin'))

@app.route('/edit_affectation/<id>', methods = ['POST', 'GET'])
def get_affectation(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM affectation WHERE affectation_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('admin/edit_affectation.html', affectation = data[0])


@app.route('/update_affectation/<id>', methods=['POST'])
def update_affectation(id):
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
        nom_appartement = request.form['nom_appartement']
        adresse_appartement = request.form['adresse_appartement']
        complement_appartement = request.form['complement_appartement']
        ville_appartement = request.form['ville_appartement']
        codepostal_appartement = request.form['codepostal_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        depot_appartement = request.form['depot_appartement']
        datee_appartement = request.form['datee_appartement']
        dates_appartement = request.form['dates_appartement']
        edl_appartement = request.form['edl_appartement']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE affectation
            SET nom_locataire = %s,
                prenom_locataire = %s,
                nom_appartement = %s,
                adresse_appartement = %s,
                complement_appartement = %s,
                ville_appartement = %s,
                codepostal_appartement = %s,
                charges_appartement = %s,
                loyer_appartement = %s,
                depot_appartement = %s,
                datee_appartement = %s,
                dates_appartement = %s,
                edl_appartement = %s
            WHERE affectation_id = %s
        """, (nom_locataire, prenom_locataire, nom_appartement, adresse_appartement,complement_appartement, ville_appartement, codepostal_appartement, charges_appartement, loyer_appartement, depot_appartement,datee_appartement,dates_appartement, edl_appartement, id))
        flash('L`affectation a bien été modifiée !')
        conn.commit()
        return redirect(url_for('Admin'))
 
@app.route('/delete_affectation/<string:id>', methods = ['POST','GET'])
def delete_affectation(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM affectation WHERE affectation_id = {0}'.format(id))
    conn.commit()
    flash('L`affectation a bien été supprimé !')
    return redirect(url_for('Admin'))





if __name__ == "__main__":
    app.run(debug=True)