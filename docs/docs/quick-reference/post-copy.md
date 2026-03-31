---
render_macros: false
---

# Post-Copy Checklist

??? note "Audience: Project Developers"

    This checklist is for project developers adding a new ETL process to an existing module in a workflow project.
    It assumes you will update committed project files, tests, and documentation in the target repository.

After running `copier copy`, see `.copier-answers/post-copier-todos/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.md` for next steps on implementing your ETL process in the project. You can copy-paste the contents of that file into a GitHub issue or a project management tool to track the implementation of the ETL process.

{%
    include-markdown "../../../template/.copier-answers/post-copier-todos/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.md.jinja"
    heading-offset=1
%}
