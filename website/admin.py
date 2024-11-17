from flask import Blueprint, render_template, redirect
from urllib.parse import quote
import os

admin = Blueprint('admin', __name__)

@admin.route('/home')
def home():
    return render_template("admin/home.html")