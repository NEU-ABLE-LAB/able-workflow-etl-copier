# Quick Reference

Apply this Copier template to an existing [`able-workflow-copier`]({{ able_workflow_copier_docs }}) project (i.e., `./`) where you havea already created a `datasets/`, `features/`, or `models/` module with [`able-workflow-module-copier`]({{ able_workflow_module_copier_docs }}) to create a new Snakemake rule with the following commands:

```bash
copier copy --trust {{ able_workflow_etl_copier_repo }}.git ./
```

{% raw %}

If this template has been updated and you would like to apply those updates to your project, run the following command replacing `{{ module_type }}`, `{{ module_name }}`, and `{{ etl_name }}` with the ETL process you would like to update. You can see all the Copier templates that have been applied to your project in the `./copier-answers/` directory. (DO NOT EDIT THESE FILES.)

```bash
copier update --trust --answers-file ".copier-answers/etl-{{ module_type }}-{{ module_name }}-{{ etl_name }}.yml" ./
```

{% endraw %}
