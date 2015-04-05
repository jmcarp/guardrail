Using guardrail with Flask and SQLAlchemy
=========================================

This is a minimal example of using guardian to manage object-level permissions
for an application powered by Flask and SQLAlchemy. The application contains
two models: `User` and `Post`. The `User` model is designated as a permissions
agent and the `Post` model as a `Target`, so that users can have permissions
on posts.

The application exposes two views: `view_post`, which requires `read`
permission, and `edit_post`, which requires `write` permission. Permissions are
controlled with the `has_post_permission` decorator factory, which raises a 403
error unless the current user has the specific permission on the post identified
by the URL:

.. code-block:: python

    @has_post_permission('read')
    @app.route('/posts/<id>/')
    def view_post(agent, target, **kwargs):
        ...

This application is just a toy and doesn't implement a real authentication
system. Instead, it creates one user and one post on starting up, and assigns
the user `read` permission on the post. All requests are assumed to come from
this auto-created user. Because the user has `read` permission on the post,
requests to `view_post` are authorized:

.. code-block::

    $ http localhost:5000/posts/1/

    HTTP/1.0 200 OK
    Content-Length: 67
    Content-Type: application/json
    Date: Sun, 05 Apr 2015 16:36:06 GMT
    Server: Werkzeug/0.10.1 Python/2.7.9

    {
        "content": "dedicated to...",
        "title": "death on two legs"
    }


But since the `edit_post` endpoint requires `write` permission, `PUT` requests
are rejected:

.. code-block::

    $ http -v PUT http://localhost:5000/posts/1/ content=newtext

    PUT /posts/1/ HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 22
    Content-Type: application/json
    Host: localhost:5000
    User-Agent: HTTPie/0.9.2

    {
        "content": "newtext"
    }

    HTTP/1.0 403 FORBIDDEN
    Content-Length: 234
    Content-Type: text/html
    Date: Sun, 05 Apr 2015 16:37:48 GMT
    Server: Werkzeug/0.10.1 Python/2.7.9

    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
    <title>403 Forbidden</title>
    <h1>Forbidden</h1>
    <p>You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.</p>
