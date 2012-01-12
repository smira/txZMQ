from zmq.core import constants


def getSocketType(socketNumber):
    return {
        constants.REQ: "request",
        constants.REP: "reply",
        constants.PUB: "pulish",
        constants.SUB: "subscribe",
        constants.DEALER: "dealer",
        constants.ROUTER: "router",
        constants.XREQ: "xrequest",
        constants.XREP: "xreply",
        constants.PUSH: "push",
        constants.PULL: "pull",
        constants.PAIR: "pair",
    }[socketNumber]


def getDottedClassName(instance):
    parts = repr(instance.__class__).split("'")
    if len(parts) >= 2:
        return parts[1]
    return instance


def buildErrorMessage(err):
    message = str(err)
    if len(err.args) > 0:
        message = err.args[0]
    return "%s: %s" % (getDottedClassName(err), message)
