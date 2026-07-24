import os
def get_pipeline_device():
    import torch

    if torch.cuda.is_available():
        return 0
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return -1


def pipeline_options():
    options = {"device": get_pipeline_device()}
    token = os.getenv("HF_TOKEN")
    if token:
        options["token"] = token
    return options
