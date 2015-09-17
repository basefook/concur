def includeme(config):
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    config.add_jinja2_search_path('concur:web/templates', name='.html')
    config.include('.urls')
