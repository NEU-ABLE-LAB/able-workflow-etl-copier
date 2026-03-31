# Quick Reference

??? note "Audience: Project Developers"

    This section is for project developers applying `able-workflow-etl-copier` to an existing workflow project.
    If you are maintaining the template itself, use this repository's contributing documentation instead.

Apply this Copier template to an existing [`able-workflow-copier`]({{ able_workflow_copier_docs }}) project (i.e., `./`) where you have already created a `datasets/`, `features/`, or `models/` module with [`able-workflow-module-copier`]({{ able_workflow_module_copier_docs }}) to create a new ETL process with the following commands:

```bash
copier copy --trust {{ able_workflow_etl_copier_repo }}.git ./
```

{% raw %}

If this template has been updated and you would like to apply those updates to your project, run the following command replacing `{{ module_type }}`, `{{ module_name }}`, and `{{ etl_name }}` with the ETL process you would like to update. You can see all the Copier templates that have been applied to your project in the `./copier-answers/` directory. (DO NOT EDIT THESE FILES.)

```bash
copier update --trust --answers-file ".copier-answers/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.yml" ./
```

{% endraw %}
