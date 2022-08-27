STRUCTURE:

- docs: contains documentation for entire project
- data: contains postgres database files
- backend: contains flask apps
    - flask
        - home: home page with links
        - database: list of all tables, views, triggers, functions etc, that can be listed, and tables and views can be viewed, filtered and editing data
        - actions: page with business action modules
            - add client
            - add sku
            - add component
            - add order
            - change order
            ...
        - report: page with reports
        - about: about page
- frontend:
    - html
    - css
    - js?
- services: contains python code with business logic
    - dump: module for creating backup of database
- log: contains logs of app