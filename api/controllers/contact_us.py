from api import Blueprint, cur, request, secure_filename, os, app, uuid, ALLOWED_EXTENSIONS, conn, psycopg2, datetime, send_file
from exceptions import MissingFormDataError, DatabaseError

contact_us_route = Blueprint('contact_us_route', __name__)


class ContactUs:

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @contact_us_route.route('/insert-crm', methods=['POST'])
    def insert_crm():
        expected_keys = {'name', 'email', 'subject', 'department', 'priority', 'message', 'attachments'}
    
        form_data = request.form
        
        form_keys = set(form_data.keys())
        unexpected_keys = form_keys - expected_keys
        if unexpected_keys:
            raise MissingFormDataError(f"Unexpected fields provided: {', '.join(unexpected_keys)}")
        
        file = request.files.get('attachments')

        if not file or not ContactUs.allowed_file(file.filename):
            raise MissingFormDataError("Invalid file or no file selected")
        
        unique_filename = ""
        if file:
            if file.filename == '':
                raise MissingFormDataError("No selected file")
            
            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

        # name = form_data['name'] + ' opportunity'
        time_now = datetime.datetime.now()
        id_partner = ""
        try:
            cur.execute("SELECT * FROM res_partner WHERE email = %s", (form_data['email'],))
            partner_records = cur.fetchall()

            if not partner_records:
                cur.execute("INSERT INTO res_partner (name, email, active) VALUES (%s, %s, %s) RETURNING id", (form_data['name'], form_data['email'], True))
                id_partner = cur.fetchone()[0]
            else:
                id_partner = partner_records[0][0]

            cur.execute('''
                INSERT INTO crm_lead (
                        partner_id,
                        user_id, 
                        team_id,
                        company_id,
                        stage_id,
                        name, 
                        email_from, 
                        contact_name,
                        type,
                        active,
                        date_open,
                        date_last_stage_update,
                        create_date,
                        write_date,
                        description,
                        docs_file,
                        priority)
                VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
            ''', (id_partner,
                1, 
                1,
                1,
                1,
                form_data['subject'], 
                form_data['email'], 
                form_data['name'],
                "opportunity",
                True,
                time_now,
                time_now,
                time_now,
                time_now,
                form_data['message'],
                unique_filename,
                form_data['priority']
                )) 
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise DatabaseError(f"Error inserting data: {e}")

        
        return {
            "status": 200,
            "message": "success"
        }

    @contact_us_route.route('/download-attachment/<path:filename>', methods=['GET'])
    def download_attachment(filename):
        path = f"../attachments/{filename}"
        try:
            return send_file(path, as_attachment=True)
        except FileNotFoundError:
            return "File not found", 404
