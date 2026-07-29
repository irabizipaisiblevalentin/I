# urubuga/ssr.i — Server-Side Rendering
# Uburyo bwo Gukora SSR na SSG

shyiramo "json"
shyiramo "filesystem"

# ── UrubugaSSR — Server-Side Rendering ──────────────────────────

urwego UrubugaSSR
    templates: {}
    components: {}

    umurimo __init__(self)
        self.templates = {}
        self.components = {}
    iherezo

    umurimo shakisha_template(self, izina: umuntu, path: umuntu) -> ubusa
        self.templates[izina] = path
    iherezo

    umurimo shakisha_component(self, izina: umuntu, handler: ubusa) -> ubusa
        self.components[izina] = handler
    iherezo

    umurimo render(self, izina: umuntu, ibiciro: {}) -> umuntu
        shyira path = self.templates.get(izina, "")
        niba path == ""
            subira "<h1>Ikosa: Template '" + izina + "' ntibonetse</h1>"
        iherezo
        
        shyira inkuru = filesystem.read(path)
        subira self._render_string(inkuru, ibiciro)
    iherezo

    umurimo render_string(self, inkuru: umuntu, ibiciro: {}) -> umuntu
        subira self._render_string(inkuru, ibiciro)
    iherezo

    umurimo _render_string(self, inkuru: umuntu, ibiciro: {}) -> umuntu
        shyira result = inkuru
        
        # Process components <ComponentName props... />
        result = self._process_components(result, ibiciro)
        
        # Process conditionals {{#if condition}}...{{/if}}
        result = self._process_conditionals(result, ibiciro)
        
        # Process loops {{#each items}}...{{/each}}
        result = self._process_loops(result, ibiciro)
        
        # Process variables {{ variable }}
        buri izina in ibiciro.keys()
            agaciro = ibiciro[izina]
            niba type(agaciro) == type("")
                result = text.replace(result, "{{ " + izina + " }}", agaciro)
                result = text.replace(result, "{{" + izina + "}}", agaciro)
            iherezo
        iherezo
        
        subira result
    iherezo

    umurimo _process_components(self, inkuru: umuntu, ibiciro: {}) -> umuntu
        # Process <ComponentName prop="value" />
        shyira result = inkuru
        buri izina in self.components.keys()
            shyira tag = "<" + izina
            niba text.contains(result, tag)
                # Extract props
                shyira start = text.index(result, tag)
                shyira end = text.index(result, "/>")
                niba start != -1 kandi end != -1
                    shyira component_str = result[start:end + 2]
                    shyira component_html = self.components[izina](ibiciro)
                    result = text.replace(result, component_str, component_html)
                iherezo
            iherezo
        iherezo
        subira result
    iherezo

    umurimo _process_conditionals(self, inkuru: umuntu, ibiciro: {}) -> umuntu
        shyira result = inkuru
        
        # Process {{#if condition}}...{{/if}}
        wihuse text.contains(result, "{{#if")
            shyira start = text.index(result, "{{#if")
            shyira condition_end = text.index(result, "}}", start)
            shyira condition = text.substring(result, start + 5, condition_end)
            shyira end = text.index(result, "{{/if}}")
            
            niba start != -1 kandi condition_end != -1 kandi end != -1
                shyira inner = text.substring(result, condition_end + 2, end)
                shyira full = text.substring(result, start, end + 6)
                
                # Check condition
                shyira condition_value = ibiciro.get(text.strip(condition), ubusa)
                niba condition_value == ukuri
                    result = text.replace(result, full, inner)
                cyangwa
                    result = text.replace(result, full, "")
                iherezo
            iherezo
        iherezo
        
        subira result
    iherezo

    umurimo _process_loops(self, inkuru: umuntu, ibiciro: {}) -> umuntu
        shyira result = inkuru
        
        # Process {{#each items}}...{{/each}}
        wihuse text.contains(result, "{{#each")
            shyira start = text.index(result, "{{#each")
            shyira name_end = text.index(result, "}}", start)
            shyira name = text.substring(result, start + 7, name_end)
            shyira end = text.index(result, "{{/each}}")
            
            niba start != -1 kandi name_end != -1 kandi end != -1
                shyira inner = text.substring(result, name_end + 2, end)
                shyira full = text.substring(result, start, end + 8)
                shyira items = ibiciro.get(text.strip(name), [])
                
                shyira loop_result = ""
                buri item in items
                    shyira item_html = inner
                    # Replace {{this}} with item
                    niba type(item) == type("")
                        item_html = text.replace(item_html, "{{this}}", item)
                    iherezo
                    loop_result = loop_result + item_html
                iherezo
                
                result = text.replace(result, full, loop_result)
            iherezo
        iherezo
        
        subira result
    iherezo
iherezo


# ── UrubugaSSG — Static Site Generation ──────────────────────────

urwego UrubugaSSG
    ssr: ubusa
    output_dir: umuntu

    umurimo __init__(self, ssr: ubusa, output_dir: umuntu)
        self.ssr = ssr
        self.output_dir = output_dir
    iherezo

    umurimo generate(self, routes: {}) -> []
        shyira generated = []
        
        buri route in routes.keys()
            shyira data = routes[route]
            shyira html = self.ssr.render(data.get("template", ""), data.get("data", {}))
            shyira file_path = self.output_dir + route
            
            # Create directory
            filesystem.mkdir(self.output_dir, ukuri)
            
            # Write file
            filesystem.write(file_path, html)
            
            generated.append(file_path)
        iherezo
        
        subira generated
    iherezo

    umurimo generate_page(self, path: umuntu, template: umuntu, data: {}) -> umuntu
        shyira html = self.ssr.render(template, data)
        shyira file_path = self.output_dir + path
        
        filesystem.mkdir(self.output_dir, ukuri)
        filesystem.write(file_path, html)
        
        subira file_path
    iherezo
iherezo
