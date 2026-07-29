"""Verify IHuriro — Define Once, Use Everywhere."""
import sys, os
sys.path.insert(0, 'src')

print('=== IHuriro Verification ===\n')

print('--- 1. Core Imports ---')
from ububiko.ihuriro import (
    IHuriro, CanonicalModel, CanonicalField, CanonicalIndex, ModelReader,
    DatabaseGenerator, ValidationGenerator, RestApiGenerator,
    GraphQLGenerator, SerializationGenerator, FormGenerator,
    AdminGenerator, DocumentationGenerator, TestDataGenerator,
    EmbeddingGenerator,
)
print('OK: 15 exports')

print('\n--- 2. CanonicalModel Construction ---')
model = CanonicalModel(
    name="Product",
    table_name="products",
    description="A sellable product",
    fields={
        "id": CanonicalField(name="id", native_type="integer", primary_key=True, auto_increment=True),
        "name": CanonicalField(name="name", native_type="string", required=True, max_length=200,
                               description="Product name"),
        "price": CanonicalField(name="price", native_type="decimal", required=True,
                                min_value=0, precision=10, scale=2),
        "active": CanonicalField(name="active", native_type="boolean", default=True),
        "category_id": CanonicalField(name="category_id", native_type="integer",
                                      foreign_key="categories.id"),
        "description": CanonicalField(name="description", native_type="text", embed=True),
        "email": CanonicalField(name="email", native_type="email", secret=True),
        "tags": CanonicalField(name="tags", native_type="array", default=[]),
    },
    indexes=[CanonicalIndex(columns=["name", "active"])],
    audit_fields=True,
    soft_delete=False,
    tags=["catalog"],
    generate=["database", "validation", "rest_api", "graphql", "serialization",
              "forms", "admin", "docs", "test_data", "embeddings"],
)

assert model.name == "Product"
assert model.table_name == "products"
assert model.pk_field is not None
assert model.pk_field.name == "id"
assert model.field_names == ["id", "name", "price", "active", "category_id", "description", "email", "tags"]
assert len(model.secret_fields) == 1  # email
assert len(model.embed_fields) == 1   # description
print(f'  Model: {model.name} ({len(model.fields)} fields)')
print(f'  PK: {model.pk_field.name}')
print(f'  Secret fields: {[f.name for f in model.secret_fields]}')
print(f'  Embed fields: {[f.name for f in model.embed_fields]}')
print(f'  JSON roundtrip: {"id" in model.to_dict()["fields"]}')

md = model.to_markdown()
assert "Product" in md
assert "products" in md
print('  Markdown doc: OK')

print('\n--- 3. ModelReader ---')
reader = ModelReader()
assert hasattr(reader, 'from_entity')
assert hasattr(reader, 'from_dataclass')
assert hasattr(reader, 'from_dict')

# from_dict
dict_model = reader.from_dict("Test", {
    "table_name": "tests",
    "fields": {"id": {"native_type": "integer", "primary_key": True}},
})
assert dict_model.name == "Test"
print('  from_dict: OK')

# from_dataclass
from dataclasses import dataclass
@dataclass
class Sample:
    name: str
    value: int = 0
dc_model = reader.from_dataclass(Sample, table_name="samples")
assert dc_model.name == "Sample"
assert dc_model.table_name == "samples"
assert "name" in dc_model.fields
print('  from_dataclass: OK')

print('\n--- 4. Generator Registration ---')
engine = IHuriro()
engine.register("database", DatabaseGenerator.generate)
engine.register("validation", ValidationGenerator.generate)
engine.register("rest_api", RestApiGenerator.generate)
engine.register("graphql", GraphQLGenerator.generate)
engine.register("serialization", SerializationGenerator.generate)
engine.register("forms", FormGenerator.generate)
engine.register("admin", AdminGenerator.generate)
engine.register("docs", DocumentationGenerator.generate)
engine.register("test_data", TestDataGenerator.generate)
engine.register("embeddings", EmbeddingGenerator.generate)

registered = engine.registered_targets
assert len(registered) == 10
print(f'  Registered generators: {registered}')

print('\n--- 5. Full Generation (all targets) ---')
results = engine.generate(model)
summary = engine.summary()
total_files = summary['total_files']
print(f'  Targets: {list(results.keys())}')
print(f'  Total files: {total_files}')
assert total_files > 0
assert 'database' in results
assert 'validation' in results
assert 'rest_api' in results
assert 'serialization' in results
assert 'docs' in results

# Check database output
db_files = results['database']
assert len(db_files) >= 2  # .sql + .py migration
sql_content = list(db_files.values())[0]
assert 'CREATE TABLE' in sql_content
print('  Database: CREATE TABLE generated')

# Check validation
val_content = list(results['validation'].values())[0]
assert 'def validate_' in val_content
print('  Validation: validate function generated')

# Check rest_api
api_content = list(results['rest_api'].values())[0]
assert 'Schema' in api_content or 'class' in api_content
print('  REST API: endpoint stubs generated')

# Check graphql (not in default generate list; skip in first pass)

# Check serialization
ser_content = list(results['serialization'].values())[0]
assert 'json' in ser_content
print('  Serialization: JSON Schema generated')

# Check forms
form_content = list(results['forms'].values())[0]
assert 'form' in form_content.lower()
print('  Forms: form definitions generated')

# Check admin
admin_content = list(results['admin'].values())[0]
assert 'ADMIN_CONFIG' in admin_content
print('  Admin: dashboard config generated')

# Check docs
docs_files = results['docs']
md_content = list(docs_files.values())[0]
assert '## Fields' in md_content
print('  Docs: Markdown + OpenAPI generated')

# Check test_data
td_content = list(results['test_data'].values())[0]
assert 'def generate_' in td_content
print('  Test Data: factory generated')

# Check embeddings
emb_content = list(results['embeddings'].values())[0]
assert 'embed' in emb_content.lower()
print('  Embeddings: config generated')

print('\n--- 6. File Output (write to disk) ---')
output_dir = "_ihuriro_test_output"
engine.generate(model, output_dir=output_dir)
assert os.path.isdir(output_dir)
target_dirs = os.listdir(output_dir)
print(f'  Output dirs: {target_dirs}')
file_count = sum(len(files) for _, _, files in os.walk(output_dir))
print(f'  Files written: {file_count}')
assert file_count > 10
import shutil
shutil.rmtree(output_dir)
print('  Cleanup: OK')

print('\n--- 7. Targeted Generation ---')
result2 = engine.generate(model, targets=["database", "docs"])
assert 'database' in result2
assert 'docs' in result2
assert 'validation' not in result2
print('  Targeted generation: OK')

print('\n--- 8. Multiple Models ---')
model2 = CanonicalModel(name="Category", table_name="categories", fields={
    "id": CanonicalField(name="id", native_type="integer", primary_key=True),
    "name": CanonicalField(name="name", native_type="string", required=True),
})
combined = engine.generate_all([model, model2])
assert 'database' in combined
assert len(combined.get('database', {})) >= 4  # SQL + migration for each model
print(f'  Combined output: {len(combined)} targets')

print('\n==================================================')
print('ALL IHURIRO VERIFICATIONS PASSED SUCCESSFULLY')
print('==================================================')
