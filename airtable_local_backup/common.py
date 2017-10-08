"""Common functions for airtable_local_backup."""
def _findkeys(node, kv):
    """
    Traverses a json object of indeterminate depth looking for a particular
    key.
    """
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x
