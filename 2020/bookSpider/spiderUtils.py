def get_page_elements(base_bs, element_json):
    results = []
    if not isinstance(element_json, list):
        element_json = [element_json]
    for element in element_json:
        bs = base_bs.find_all(element['name'], element['attrs'])
        sub = element['sub']
        stack = bs
        while sub is not None:
            sub_stack = []
            while len(stack) > 0:
                cur = stack.pop()
                if "attrs" in sub:
                    children = cur.find_all(sub['name'], sub["attrs"])
                else:
                    children = cur.find_all(sub['name'])
                sub_stack = sub_stack + children
            stack = sub_stack
            if "sub" in sub:
                sub = sub['sub']
            else:
                sub = None
        results = results + stack
    return results

