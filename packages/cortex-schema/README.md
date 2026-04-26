# @cortex/schema

JSON Schema for `cortex.yml` — powers IDE autocomplete and validation.

## Use it in VS Code

Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml),
then add to your `cortex.yml`:

```yaml
# yaml-language-server: $schema=https://cortex.dev/schema/v1.json
version: 1
identity:
  name: "..."
  ...
```

You'll get:
- Autocomplete on every config key
- Inline documentation when you hover
- Real-time validation (red squiggles on typos)
- Enum suggestions for fields like `palette`, `status`, `accent`

## Or in JetBrains IDEs

Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings →
add `https://cortex.dev/schema/v1.json` mapped to `cortex.yml`.

## Programmatic validation

The same schema is used by `cortex validate` (Python). If you want to validate
in another language:

```bash
npm i ajv
node -e "
  const Ajv = require('ajv');
  const ajv = new Ajv();
  const schema = require('./schema.json');
  const config = require('./cortex.yml');  // requires yaml loader
  const valid = ajv.validate(schema, config);
  console.log(valid ? 'OK' : ajv.errors);
"
```

## License

MIT.
