import hashlib
import copy

from flask import render_template_string

from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.flags import BaseFlag, CTFdStaticFlag, FLAG_CLASSES

# How long the flag should be
FLAG_LENGTH = 8

PLUGIN_PAGE="""
{% extends "admin/base.html" %}

{% block content %}
<div class="jumbotron">
	<div class="container">
		<h1>User Unique Flags</h1>
	</div>
</div>
<div class="container">
    <p>This plugin adds a new type of flag ("individual") that is different for each user</p>
    <p>The flag's value is a secret, as usual.
       The user's username is then taken, appended to the secret, hashed with sha1 then the first FLAG_LENGTH characters are taken.
       The correct becomes flag{...}.</p>
    <p>The current flag length is {{flag_length}}</p>
    <p>For example, if the secret is "BIKE" and the user is "alice", "BIKEalice" is hashed</p>
    <p>
        <code>&gt; echo -n "BIKEalice" | sha1sum</code>
        <br>
        <code>3c53c2784cfc87efeb78ae5b9398ffb4a3a6895c</code>
    </p>
</div>
{% endblock content %}
"""

def create_individual_flag(secret, user):
    print(f"Merging secret '{secret}' and '{user.name}'")
    merged = "".join([secret, user.name])
    m = hashlib.sha1()
    m.update(bytes(merged, "utf-8"))
    hashed = m.hexdigest()
    flag = "flag{" + hashed[0:FLAG_LENGTH] + "}"
    print(f"Flag for '{user.name}' is {flag}")
    return flag

class IndividualFlag(BaseFlag):
    name = "individual"
    templates = {
        "create": "/plugins/user_unique_flags/assets/individual/create.html",
        "update": "/plugins/user_unique_flags/assets/individual/edit.html",
    }
    
    @staticmethod
    def compare(chal_key_obj, provided):
        individual_flag = create_individual_flag(chal_key_obj.content, get_current_user())
        chal_key_obj = copy.deepcopy(chal_key_obj)
        chal_key_obj.content = individual_flag
        return CTFdStaticFlag.compare(chal_key_obj, provided)
    

def load(app):
    # Register route for plugin page
    @app.route("/admin/user_unique_flags", methods=["GET"])
    @admins_only
    def user_unique_flags_page():
        return render_template_string(PLUGIN_PAGE, flag_length=FLAG_LENGTH)
    
    # Register custom challenge type
    FLAG_CLASSES[IndividualFlag.name] = IndividualFlag
    # Register assets
    register_plugin_assets_directory(app, base_path="/plugins/user_unique_flags/assets")
