# urubuga/graphql.i — GraphQL Server
# Uburyo bwo Gukora GraphQL API

shyiramo "json"

# ── UrubugaGraphQL — GraphQL Schema ──────────────────────────────

urwego UrubugaGraphQLSchema
    queries: {}
    mutations: {}
    subscriptions: {}
    types: {}

    umurimo __init__(self)
        self.queries = {}
        self.mutations = {}
        self.subscriptions = {}
        self.types = {}
    iherezo

    umurimo query(self, izina: umuntu, ubwoko: umuntu, resolver: ubusa) -> ubusa
        self.queries[izina] = {"type": ubwoko, "resolver": resolver}
    iherezo

    umurimo mutation(self, izina: umuntu, ubwoko: umuntu, resolver: ubusa) -> ubusa
        self.mutations[izina] = {"type": ubwoko, "resolver": resolver}
    iherezo

    umurimo subscription(self, izina: umuntu, ubwoko: umuntu, resolver: ubusa) -> ubusa
        self.subscriptions[izina] = {"type": ubwoko, "resolver": resolver}
    iherezo

    umurimo register_type(self, izina: umuntu, fields: {}) -> ubusa
        self.types[izina] = fields
    iherezo

    umurimo execute(self, query: umuntu, variables: {}) -> {}
        # Simple query parser
        ibiciro = self._parse_query(query)
        
        niba ibiciro.get("type") == "query"
            results = {}
            buri field in ibiciro.get("fields", [])
                niba field in self.queries
                    results[field] = self.queries[field]["resolver"](variables)
                iherezo
            iherezo
            subira {"data": results}
        cyangwa niba ibiciro.get("type") == "mutation"
            results = {}
            buri field in ibiciro.get("fields", [])
                niba field in self.mutations
                    results[field] = self.mutations[field]["resolver"](variables)
                iherezo
            iherezo
            subira {"data": results}
        iherezo
        
        subira {"errors": [{"message": "Unknown operation type"}]}
    iherezo

    umurimo _parse_query(self, query: umuntu) -> {}
        # Simplified GraphQL query parsing
        query = text.strip(query)
        
        niba text.startswith(query, "query")
            subira {"type": "query", "fields": self._extract_fields(query)}
        cyangwa niba text.startswith(query, "mutation")
            subira {"type": "mutation", "fields": self._extract_fields(query)}
        iherezo
        
        subira {"type": "query", "fields": self._extract_fields(query)}
    iherezo

    umurimo _extract_fields(self, query: umuntu) -> []
        # Find fields between { }
        shyira start = text.index(query, "{")
        shyira end = text.rindex(query, "}")
        niba start == -1 kandi end == -1
            subira []
        iherezo
        
        shyira content = query[start + 1:end]
        shyira ibiciro = text.split(content, " ")
        subira [f for f in ibiciro if f != ""]
    iherezo

    umurimo sdl(self) -> umuntu
        # Generate Schema Definition Language
        lines = ["type Query {"]
        buri izina in self.queries.keys()
            lines.append("  " + izina + ": " + self.queries[izina]["type"])
        iherezo
        lines.append("}")
        lines.append("")
        lines.append("type Mutation {")
        buri izina in self.mutations.keys()
            lines.append("  " + izina + ": " + self.mutations[izina]["type"])
        iherezo
        lines.append("}")
        subira "\n".join(lines)
    iherezo
iherezo


# ── UrubugaGraphQL — GraphQL Endpoint Handler ────────────────────

urwego UrubugaGraphQLEndpoint
    schema: ubusa

    umurimo __init__(self, schema: ubusa)
        self.schema = schema
    iherezo

    umurimo handle(self, request: ubusa) -> {}
        shyira data = request.json_data
        niba data == ubusa
            subira {"errors": [{"message": "No query provided"}]}
        iherezo
        
        shyira query = data.get("query", "")
        shyira variables = data.get("variables", {})
        shyira operation_name = data.get("operationName", "")
        
        subira self.schema.execute(query, variables)
    iherezo
iherezo


# ── UrubugaGraphQLPlayground — Interactive Query Editor ──────────
umurimo graphql_playground() -> umuntu
    subira `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Urubuga GraphQL Playground</title>
        <style>
            body { margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; background: #1a1a2e; }
            .playground { display: grid; grid-template-columns: 1fr 1fr; height: 100vh; }
            .editor { padding: 20px; background: #16213e; color: #e2e8f0; border-right: 1px solid #333; }
            .result { padding: 20px; background: #0f3460; color: #e2e8f0; }
            textarea { width: 100%; height: 100%; background: transparent; color: #e2e8f0; border: none; resize: none; font-family: monospace; font-size: 14px; }
            button { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-bottom: 10px; }
            pre { white-space: pre-wrap; font-family: monospace; }
            h2 { color: #667eea; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="playground">
            <div class="editor">
                <h2>GraphQL Query</h2>
                <button onclick="executeQuery()">Gukora (Execute)</button>
                <textarea id="query" placeholder="Write your GraphQL query here...">{ hello }</textarea>
            </div>
            <div class="result">
                <h2>Result</h2>
                <pre id="result">Press "Gukora" to execute</pre>
            </div>
        </div>
        <script>
            async function executeQuery() {
                const query = document.getElementById('query').value;
                const result = document.getElementById('result');
                try {
                    const response = await fetch('/graphql', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query })
                    });
                    const data = await response.json();
                    result.textContent = JSON.stringify(data, null, 2);
                } catch (e) {
                    result.textContent = 'Error: ' + e.message;
                }
            }
        </script>
    </body>
    </html>
    `
iherezo
