#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class NewPost(Handler):

    def render_main(self, title="", blogpost="", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_main()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            b = BlogPost(title = title, blogpost = blogpost)
            b.put()
            post = b.key().id()

            self.redirect("/blog/" + str(post))
        else:
            error = "we need both a title and a blogpost."
            self.render_main(title, blogpost, error)


class BlogPost(db.Model):

    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Blog(Handler):

    def render_blog(self, title="",blogpost="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost "
                                "ORDER BY created DESC "
                                "LIMIT 5")

        self.render("main.html", title=title, blogpost=blogpost, error=error, blogposts=blogposts)

    def get(self):
        self.render_blog()


class ViewPostHandler(Handler):

    def get(self, id):

        blogpost = BlogPost.get_by_id(int(id))
        self.render("single.html", blogpost=blogpost)


def get_posts(limit, offset):
    posts = db.GqlQuery("SELECT * FROM BlogPost "
                        "ORDER BY created DESC "
                        "LIMIT  OFFSET ")

    self.render("main.html", title=title, blogpost=blogpost, error=error, posts=posts)


class MainPage(Handler):

    def get(self):
        self.render("newpost.html")


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
