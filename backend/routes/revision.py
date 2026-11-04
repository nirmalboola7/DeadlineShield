from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from config import UPLOAD_DIR
from store import read_db, write_db, next_id
from utils import login_required

bp=Blueprint('revision',__name__,url_prefix='/api/revision')
ALLOWED={'pdf','docx','txt'}

@bp.post('/upload')
@login_required
def upload():
    if 'file' not in request.files: return jsonify({'error':'No file was attached.'}),400
    file=request.files['file']
    if not file.filename: return jsonify({'error':'Choose a file first.'}),400
    safe=secure_filename(file.filename); ext=safe.rsplit('.',1)[-1].lower() if '.' in safe else ''
    if ext not in ALLOWED: return jsonify({'error':'Only PDF, DOCX and TXT files are allowed.'}),400
    user_dir=UPLOAD_DIR/str(g.user['user_id']); user_dir.mkdir(parents=True,exist_ok=True)
    stored=f"{uuid4().hex}_{safe}"; file.save(user_dir/stored)
    db=read_db()
    record={'file_id':next_id(db['files'],'file_id'),'user_id':g.user['user_id'],
            'file_name':safe,'stored_name':stored,'file_type':ext,'uploaded_at':datetime.now(timezone.utc).isoformat()}
    db['files'].append(record)
    # Demonstration questions only: no file contents are analysed in this first version.
    if not any(q['user_id']==g.user['user_id'] for q in db['questions']):
        samples=[
            {'question':'Define the main concepts in this subject and explain their purpose.','answer':'Write a concise definition, explain why the concept is used, and include one example.','priority':'High'},
            {'question':'Compare the important methods or approaches covered in your notes.','answer':'Present the key differences in a table and conclude when each approach is useful.','priority':'Medium'},
            {'question':'Explain one practical application from the uploaded study material.','answer':'Describe the problem, the method used, and the expected result.','priority':'Medium'}]
        for q in samples:
            db['questions'].append({'question_id':next_id(db['questions'],'question_id'),'user_id':g.user['user_id'],
                'file_id':record['file_id'],'subject':'Uploaded material',**q,'created_at':datetime.now(timezone.utc).isoformat()})
    write_db(db)
    return jsonify({'message':'File uploaded. Sample revision prompts are available; automatic document analysis is a future enhancement.','file':{'file_id':record['file_id'],'file_name':safe}}),201

@bp.get('/questions')
@login_required
def questions():
    db=read_db()
    return jsonify([q for q in db['questions'] if q['user_id']==g.user['user_id']])
