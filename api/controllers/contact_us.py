from api import Blueprint, request, send_file, jsonify,database,url,username,password,app,session
from exceptions import MissingFormDataError, DatabaseError
from validation import InsertCrmForm
import xmlrpc.client
from datetime import datetime, timedelta

contact_us_route = Blueprint('contact_us_route', __name__)
MAX_REQUESTS_PER_MINUTE = 10

class ContactUs:

    @staticmethod
    def search(db, uid, password,value,fields,model_tabels,models):
        return models.execute_kw(db, uid, password, model_tabels, 'search_read', [[[fields, '=', value]]], {'fields': ['id', 'name','email'], 'limit': 1})
    

    @staticmethod
    def search_crm(db, uid, password,value,fields,model_tabels,models):
        return models.execute_kw(db, uid, password, model_tabels, 'search_read', [[[fields, '=', value]]], {'fields': ['id', 'name'], 'limit': 1})

    @staticmethod
    def create_partner(db, uid, password,name,email_partner,phone,city,models):
        
        contact_data = {
            'name': name,
            'email': email_partner,
            'active':True,
            'phone':phone,
            'city':city
        }
        return models.execute_kw(db, uid, password, 'res.partner', 'create', [contact_data])
    
    def create_crm_tags(db, uid, password,name,models):
        
        data_crm_tag = {
            'name': name,
        }
        return models.execute_kw(db, uid, password, 'crm.tag', 'create', [data_crm_tag])

    @contact_us_route.route('/insert-crm', methods=['POST'])
    def insert_crm():
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        expected_keys = {'firstname','lastname', 'email', 'country',
                          'phone', 'priority', 'request', 'product','city'
                          }
        uid = ContactUs.authenticate(url, database, username, password)

        form_data = request.form

        crm_tags = ContactUs.search_crm(db=database,uid=uid,password=password,value=form_data['product'],fields='name',model_tabels='crm.tag',models=models)

        if crm_tags:
            id_crm_tags = crm_tags[0].get('id')
        else:
            id_partner = ContactUs.create_crm_tags(db=database,uid=uid,password=password,name=form_data['product'],models=models)
            new_partner = ContactUs.ContactUs.search_crm(db=database,uid=uid,password=password,value=form_data['product'],fields='name',model_tabels='crm.tag',models=models)
            id_crm_tags = crm_tags[0].get('id')
           

       
        form_keys = set(form_data.keys())
        unexpected_keys = form_keys - expected_keys
        if unexpected_keys:
            raise MissingFormDataError(f"Unexpected fields provided: {', '.join(unexpected_keys)}")
        
        
        partner = ContactUs.search(db=database,uid=uid,password=password,value=form_data['email'],fields='email',model_tabels='res.partner',models=models)
        
        
        if partner:
            id_part = partner[0].get('id')
            name_partner = partner[0].get('name')
            email_partner = partner[0].get('email')
        else:
            full_name = f"{form_data['firstname']} {form_data['lastname']}"
            id_partner = ContactUs.create_partner(db=database,uid=uid,password=password,name=full_name,email_partner=form_data['email'],phone=form_data['phone'],city=form_data['city'],models=models)
            new_partner = ContactUs.search(db=database,uid=uid,password=password,value=id_partner,fields='id',model_tabels='res.partner',models=models)
            id_part = new_partner[0].get('id')
            name_partner = new_partner[0].get('name')
            email_partner = new_partner[0].get('email')

        
        
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
                # 'tag_ids': [(6, 0, id_crm_tags)],
            }

            del session['csrf_token']
            
            data_crm = models.execute_kw(database, uid, password, 'crm.lead', 'create', [partner_data])
            
            models.execute_kw(database, uid, password, 'crm.lead', 'write', [[data_crm], {'tag_ids': [(id_crm_tags)]}])


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

    