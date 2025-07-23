---
render_macros: false
---

# Post-Copy Checklist

After running `copier copy`, see `.copier-answers/post-copier-todos/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.md` for next steps on implementing your rule into the project. You can copy-paste the contents of that file into a GitHub issue or a project management tool to track the implementation of the rule.

{%
    include-markdown "../../../template/.copier-answers/post-copier-todos/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.md.jinja"
    heading-offset=1
%}
