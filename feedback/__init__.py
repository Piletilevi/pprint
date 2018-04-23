class feedback():
    print("inside", __name__)
    import decorators

    def __init__(self):
        print("INSIDE", __name__, ".__init__()")

    @decorators.profiler
    @decorators.logging
    def __call__():
        print("inside", __name__, ".__call__()")




global FEEDBACK_TEMPLATE
# with open(os.path.join(BASEDIR, 'package.json'), 'r') as package_json_file:
#     global PACKAGE_JSON_DATA
#     PACKAGE_JSON_DATA = json.load(package_json_file)

fbtmpl_fn = os.path.join(BASEDIR, 'config', 'feedbackTemplate.json')
with open(fbtmpl_fn, 'r', encoding='utf-8') as feedback_template_file:
    FEEDBACK_TEMPLATE = json.load(feedback_template_file)
    FEEDBACK_TEMPLATE['feedbackToken'] = PLP_JSON_DATA.get('feedbackToken')
    FEEDBACK_TEMPLATE['operationToken'] = PLP_JSON_DATA\
        .get('operationToken')
    FEEDBACK_TEMPLATE['businessTransactionId'] = PLP_JSON_DATA\
        .get('fiscalData', {'businessTransactionId': ''})\
        .get('businessTransactionId', '')
    FEEDBACK_TEMPLATE['operation'] = PLP_JSON_DATA\
        .get('fiscalData').get('operation')
