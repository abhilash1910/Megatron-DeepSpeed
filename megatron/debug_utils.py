import torch
from packaging import version
class DebugGradientNorm:
    def __init__(self, model, layers=[]):
        self.model = model
        if layers:
            try:
                self.module2key = {model[layer]: layer for layer in layers}
            except TypeError:
                self.module2key = {getattr(model, layer): layer for layer in layers}
        else:
            self.module2key = {module: name for name, module in model.named_modules()}

    def backward_hook(self, module, grad_inputs, grad_outputs):
        min_grad_norm = min(
            grad_output.min().item() for grad_output in grad_outputs if grad_output is not None
        )
        max_grad_norm = max(
            grad_output.max().item() for grad_output in grad_outputs if grad_output is not None
        )
        total_norm = sum(
            grad_output.norm() ** 2 for grad_output in grad_outputs if grad_output is not None
        ).sqrt().item()
        module_name = self.module2key[module]
        print(f"{module_name}: total {total_norm}, min {min_grad_norm}, max {max_grad_norm}")

    def register_backward_hook(self):
        self.model.apply(self._register_backward_hook)

    def _register_backward_hook(self, module):
        if version.parse(torch.__version__) >= version.parse("1.10"):
            module.register_full_backward_hook(self.backward_hook)
        else:
            module.register_backward_hook(self.backward_hook)
