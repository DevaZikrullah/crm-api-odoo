from api import Blueprint, request,datetime, send_file, jsonify,database,url,username,password,app
from exceptions import MissingFormDataError, DatabaseError
from validation import InsertCrmForm
import xmlrpc.client

contact_us_route = Blueprint('contact_us_route', __name__)
MAX_RETRIES = 3

class ContactUs:

    @staticmethod
    def search_partner(db, uid, password,value,fields,models):
        return models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[[fields, '=', value]]], {'fields': ['id', 'name','email'], 'limit': 1})

    @staticmethod
    def create_partner(db, uid, password,name,email_partner,phone,models):
        
        contact_data = {
            'name': name,
            'email': email_partner,
            'active':True,
            'phone':phone
        }
        return models.execute_kw(db, uid, password, 'res.partner', 'create', [contact_data])

    @contact_us_route.route('/insert-crm', methods=['POST'])
    def insert_crm():
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        expected_keys = {'firstname','lastname', 'email', 'country',
                          'phone', 'priority', 'request', 'product'
                          }
        uid = ContactUs.authenticate(url, database, username, password)
    
        form_data = request.form
        
        form_keys = set(form_data.keys())
        unexpected_keys = form_keys - expected_keys
        if unexpected_keys:
            raise MissingFormDataError(f"Unexpected fields provided: {', '.join(unexpected_keys)}")
        
        partner = ContactUs.search_partner(db=database,uid=uid,password=password,value=form_data['email'],fields='email',models=models)
        
        
        if partner:
            id_part = partner[0].get('id')
            name_partner = partner[0].get('name')
            email_partner = partner[0].get('email')
        else:
            full_name = f"{form_data['firstname']} {form_data['lastname']}"
            id_partner = ContactUs.create_partner(db=database,uid=uid,password=password,name=full_name,email_partner=form_data['email'],models=models)
            new_partner = ContactUs.search_partner(db=database,uid=uid,password=password,value=id_partner,fields='id',models=models)
            id_part = new_partner[0].get('id')
            name_partner = new_partner[0].get('name')
            email_partner = new_partner[0].get('email')

        time_now = datetime.datetime.now()
        
        
        form_insert_crm = InsertCrmForm(form_data)

        if form_insert_crm.validate_on_submit():
            partner_data = {
                'partner_id':id_part,
                'name': form_data['product'],
                'user_id': uid,
                'team_id':1,
                'company_id':1,
                'email_from': email_partner,
                'priority':'2',
                'description':form_data['request'],
                'type':"opportunity",
                'active': True,
            }
            
            data_crm = models.execute_kw(database, uid, password, 'crm.lead', 'create', [partner_data])
            return jsonify({
                "message": "succses",
                "data" : data_crm
                            }), 200
        else:
            errors = {field: error[0] for field, error in form_insert_crm.errors.items()}
            return jsonify({"errors": errors}), 400

    @contact_us_route.route('/download-attachment/<path:filename>', methods=['GET'])
    def download_attachment(filename):
        path = f"../attachments/{filename}"
        try:
            return send_file(path, as_attachment=True)
        except FileNotFoundError:
            return "File not found", 404

    @staticmethod
    def authenticate(url, db, username, password):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            print('Authenticated as', username)
        else:
            raise Exception('Authentication failed')
        return uid
    
    @app.route('/api/get_csrf_token', methods=['GET'])
    def get_csrf_token():
        form = InsertCrmForm()
        return jsonify({"csrf_token": form.csrf_token.current_token})

    