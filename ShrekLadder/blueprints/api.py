from flask import Blueprint, render_template, abort, request, redirect, session, url_for, current_app
from flask.ext.login import current_user, login_user
from sqlalchemy import desc, asc
from ShrekLadder.objects import *
from ShrekLadder.config import config
from datetime import datetime

import time
import os
import zipfile
import urllib
import math

@api.route('/api/match/create', methods=['POST'])
@json_output
def create_match():
    if not current_user:
        return { 'error': True, 'reason': 'You are not logged in.' }, 401
    name = request.form.get('name')
    if not name:
        return { 'error': True, 'reason': 'All fields are required.' }, 400
    if len(name) > 100:
        return { 'error': True, 'reason': 'Fields exceed maximum permissible length.' }, 400
    
    main = Main.query.filter(Main.name == name).first()
    current_mod.main_list
    db.add(mod_list)
    db.commit()
    return { 'url': url_for("lists.view_list", list_id=mod_list.id, list_name=mod_list.name) }