## Project Setup

Create a new directory called build-a-blog, and then set up a local Git repository and a remote repository on GitHub. See the Web Caesar setup instructions if you need to review that process. Then set up a user and database in phpMyAdmin for this project. We recommend you use the name build-a-blog, but the password is up to you. Just remember that you will need to put all of that info into your database connection string. For refreshers on these parts of the process, re-visit FlickList 6 and Database Configuration. You'll also want to activate your flask-env virtual environment

## List and Create Blog Posts
If you think about it for a minute, the behavior of creating a blog post, saving it to the database, and displaying blog posts is essentially what we did with tasks in the Get It Done! example app. The main difference between the two is that the blog post submission form and blog post listings will be on separate pages in our Build-a-Blog app. Go back to your code for Get It Done!, or use ours, and use it as a model to set up the beginnings of your blog app.

First, set up the blog so that the "add a new post" form and the blog listings are on the same page, as with Get It Done!, and then separate those portions into separate routes, handler classes, and templates. For the moment, when a user submits a new post, redirect them to the main blog page.


Make sure you can say the following about your app:

- The /blog route displays all the blog posts.
- You're able to submit a new post at the /newpost route. After submitting a new post, your app displays the main blog page.
- You have two templates, one each for the /blog (main blog listings) and /newpost (post new blog entry) views. Your templates should extend a base.html template which includes some boilerplate HTML that will be used on each page.
- In your base.html template, you have some navigation links that link to the main blog page and to the add new blog page.
- If either the blog title or blog body is left empty in the new post form, the form is rendered again, with a helpful error message and any previously-entered content in the same form inputs.

## Display Individual Entries
Let's add the ability to view each blog all by itself on a webpage. Instead of creating multiple HTML files, one for each new blog post we create, we can use a single template to display a given blog's title and body. We'll designate which blog's data we want displayed by using a query param containing the id for that blog in the url. Then the request handler can dynamically grab the blog that corresponds to that id from the database and pass it to the template to generate the desired page.

There are two use cases for this functionality:

- Use Case 1: We click on a blog entry's title on the main page and go to a blog's individual entry page.
- Use Case 2: After adding a new blog post, instead of going back to the main page, we go to that blog post's individual entry page.

For both use cases we need to create the template for the page that will display an individual blog, so start by making that. All it need do is display a blog title and blog body. Next, we'll tackle the use cases one at a time.

But first, a reminder! It's been a little while since we used query params and GET requests, so it will be a useful reference and review to look at the lesson Forms in Flask, especially the section Accessing Get Request Parameters.

Use Case 1
