from flask import Flask, request, session, redirect, url_for, render_template, flash,jsonify
import psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash

 
app = Flask(__name__)
app.secret_key = 'infeco_organization'
 
DB_HOST = "dpg-chdon2e7avj0djj2jd8g-a.frankfurt-postgres.render.com"
DB_NAME = "infeco_db"
DB_USER = "infeco_1"
DB_PASS = "98lbxGgEybkXAaIMS6ggNKB45N7LQsE3"
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
 
#LOGIN AND REGISTRATION 
 
 
@app.route('/')
def home():

    if 'loggedin' in session:
    

        return render_template('home.html', username=session['username'])

    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))

        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)

            if check_password_hash(password_rs, password):

                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']

                return redirect(url_for('home'))
            else:

                flash('Incorrect username/password')
        else:

            flash('Incorrect username/password')
 
    return render_template('login/login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
   
        if account:
            flash('Ce compte existe déjà!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Adresse email invalide!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Le nom d`utilisateur doit contenir que des charactères et chiffres!')
        elif not username or not password or not email:
            flash('Remplissez tout le formulaire svp!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('Vous êtes connecté avec succées!')
    elif request.method == 'POST':

        flash('Remplissez tout le formulaire svp!')

    return render_template('login/register.html')
   
   
@app.route('/logout')
def logout():

   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)

   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   

    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        return render_template('profile.html', account=account)

    return redirect(url_for('login'))

#LOCATAIRE

@app.route('/Locataire')
def Locataire():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    l = "SELECT * FROM locataire"
    cur.execute(l)
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
 
 
@app.route('/edit_locataire/<id>', methods = ['POST', 'GET'])
def get_locataire(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM locataire WHERE locataire_id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('locataire/edit_locataire.html', locataire = data[0])
 
@app.route('/update_locataire/<id>', methods=['POST'])
def update_locataire(id):
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE locataire
            SET nom_locataire = %s,
                prenom_locataire = %s
            WHERE locataire_id = %s
        """, (nom_locataire, prenom_locataire, id))
        flash('Le locataire a bien été modifié !')
        conn.commit()
        return redirect(url_for('Appartement'))
 
@app.route('/delete_locataire/<string:id>', methods = ['POST','GET'])
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
    cur.execute(a)
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
        cur.execute("INSERT INTO appartement (nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement,charges_appartement,loyer_appartement,depot_appartement) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (nom_appartement, adresse_appartement, complement_appartement, ville_appartement, codepostal_appartement,charges_appartement,loyer_appartement,depot_appartement))
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
    cur.execute(a)
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
    cur.execute(p)
    list_paiement = cur.fetchall()
    cur.execute("SELECT * FROM affectation ORDER BY affectation_id")
    affectation_paiement = cur.fetchall() 
    return render_template('paiement/paiement.html', list_paiement = list_paiement, affectation_paiement = affectation_paiement)
 
@app.route('/add_paiement', methods=['POST'])
def add_paiement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        prenom_locataire = request.form['prenom_locataire']
        nom_appartement = request.form['nom_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        mois_paiement = request.form['mois_paiement']
        cur.execute("INSERT INTO paiement (nom_locataire, prenom_locataire, nom_appartement, charges_appartement,loyer_appartement,mois_paiement) VALUES (%s,%s,%s,%s,%s,%s)", (nom_locataire, prenom_locataire, nom_appartement, charges_appartement,loyer_appartement,mois_paiement))
        conn.commit()
        flash('Le paiement a bien été ajouté !')
        return redirect(url_for('Paiement'))

@app.route("/get_numero_affectation",methods=["POST","GET"])
def get_numero_affectation():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        numero_affectation = request.form['numero_affectation']
        print(numero_affectation)
        cur.execute("SELECT * FROM affectation WHERE nom_locataire = %s", [numero_affectation])
        infos_affectation = cur.fetchall()
    return jsonify({'htmlresponse': render_template('paiement/numero_affectation.html', infos_affectation=infos_affectation)})
 
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
        nom_locataire = request.form['nom_paiement']
        prenom_locataire = request.form['prenom_paiement']
        nom_appartement = request.form['nom_appartement']
        charges_appartement = request.form['charges_appartement']
        loyer_appartement = request.form['loyer_appartement']
        mois_paiement = request.form['mois_paiement']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE paiement
            SET nom_locataire = %s,
                prenom_locataire = %s,
                nom_appartement = %s,
                nom_appartement = %s,
                charges_appartement = %s,
                loyer_appartement = %s,
                mois_paiement = %s
            WHERE paiment_id = %s
        """, (nom_locataire, prenom_locataire, nom_appartement, charges_appartement,loyer_appartement,mois_paiement, id))
        flash('Le paiement a bien été modifié !')
        conn.commit()
        return redirect(url_for('Paiement'))
 
@app.route('/delete_paiement/<string:id>', methods = ['POST','GET'])
def delete_paiement(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM paiement WHERE paiement_id = {0}'.format(id))
    conn.commit()
    flash('Le paiement a bien été supprimé !')
    return redirect(url_for('Paiement'))

#ADMIN 


@app.route('/Admin')
def Admin():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    la = "SELECT * FROM affectation"
    cur.execute(la)
    list_des_affectations = cur.fetchall()
    cur.execute("SELECT * FROM locataire ORDER BY locataire_id")
    locataire = cur.fetchall() 
    cur.execute("SELECT * FROM appartement ORDER BY appartement_id")
    appartement = cur.fetchall() 
    return render_template('admin/admin.html', list_des_affectations = list_des_affectations, locataire=locataire, appartement = appartement)


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
    
@app.route("/get_nom_locataire",methods=["POST","GET"])
def get_nom_locataire():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        nom_locataire = request.form['nom_locataire']
        print(nom_locataire)
        cur.execute("SELECT * FROM locataire WHERE nom_locataire = %s", [nom_locataire])
        infos_locataire = cur.fetchall()
    return jsonify({'htmlresponse': render_template('admin/locataire.html', infos_locataire=infos_locataire)})

@app.route("/get_nom_appartement",methods=["POST","GET"])
def get_nom_appartement():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)    
    if request.method == 'POST':
        nom_appartement = request.form['nom_appartement']
        print(nom_appartement)
        cur.execute("SELECT * FROM appartement WHERE nom_appartement = %s", [nom_appartement])
        infos_appartement= cur.fetchall()
    return jsonify({'htmlresponse': render_template('admin/appartement.html', infos_appartement=infos_appartement)})

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