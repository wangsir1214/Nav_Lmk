"""Fixed-vocabulary cosine-hard VLAD; FP32 NumPy aggregation with optional PyTorch loading."""
from pathlib import Path
import numpy as np


def unit(x, axis=-1):
    return x / np.maximum(np.linalg.norm(x, axis=axis, keepdims=True), np.float32(1e-12))


def aggregate(patches, centers):
    patches = np.asarray(patches, dtype=np.float32)
    centers = np.asarray(centers, dtype=np.float32)
    if patches.ndim != 2 or centers.ndim != 2 or patches.shape[1] != centers.shape[1] or not len(patches) or not len(centers):
        raise ValueError('Invalid [patch,dim]/[cluster,dim] arrays')
    if not np.isfinite(patches).all() or not np.isfinite(centers).all():
        raise ValueError('Non-finite descriptor or vocabulary')
    if np.any(np.linalg.norm(patches, axis=1) == 0) or np.any(np.linalg.norm(centers, axis=1) == 0):
        raise ValueError('Zero descriptor or vocabulary center')
    patches = unit(patches)
    # Normalize centers only for cosine assignment; residuals use stored centers.
    labels = np.argmax(patches @ unit(centers).T, axis=1)
    residuals = np.zeros_like(centers, dtype=np.float32)
    for k in range(len(centers)):
        selected = patches[labels == k]
        if len(selected):
            residuals[k] = (selected - centers[k]).sum(axis=0, dtype=np.float32)
    descriptor = unit(unit(residuals).reshape(-1))
    if not np.isfinite(descriptor).all() or np.linalg.norm(descriptor) == 0:
        raise ValueError('Degenerate VLAD vector')
    return descriptor.astype(np.float32, copy=False)


def load_centers(path):
    import torch
    obj = torch.load(Path(path), map_location='cpu', weights_only=True)
    if not isinstance(obj, torch.Tensor) or tuple(obj.shape) != (32, 1536):
        raise ValueError('Expected raw Tensor [32,1536] for g14/l31/value/c32/urban')
    centers = obj.detach().float().numpy()
    if not np.isfinite(centers).all() or np.any(np.linalg.norm(centers, axis=1) == 0):
        raise ValueError('Invalid cluster centers')
    return centers


def load_input_png(path):
    """No resize/crop here: consume the provenance-checked 448 RGB PNG."""
    import torch
    from PIL import Image
    with Image.open(path) as image:
        if image.format != 'PNG' or image.mode != 'RGB' or image.size != (448, 448):
            raise ValueError('Expected RGB PNG 448x448')
        rgb = np.array(image, dtype=np.float32) / np.float32(255)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    return torch.from_numpy(np.ascontiguousarray(((rgb - mean) / std).transpose(2, 0, 1))).unsqueeze(0)


class G14ValueExtractor:
    """Load a pinned local DINOv2 checkout and an explicit local G/14 checkpoint."""
    def __init__(self, source_dir, weights, device='cuda'):
        import torch
        self.torch = torch
        self.device = device
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        self.model = torch.hub.load(str(Path(source_dir).resolve()), 'dinov2_vitg14',
                                    source='local', pretrained=False)
        state = torch.load(weights, map_location='cpu', weights_only=True)
        self.model.load_state_dict(state, strict=True)
        del state
        if self.model.embed_dim != 1536 or len(self.model.blocks) != 40 or self.model.num_register_tokens != 0:
            raise ValueError('Unexpected model architecture')
        self.model.eval().float().to(device)
        self.value = None
        self.hook = self.model.blocks[31].attn.qkv.register_forward_hook(self._capture)

    def _capture(self, module, inputs, output):
        self.value = output[..., 3072:4608].detach()

    def __call__(self, image):
        torch = self.torch
        if tuple(image.shape) != (1, 3, 448, 448):
            raise ValueError('Expected one image [1,3,448,448]')
        self.value = None
        with torch.inference_mode():
            self.model(image.to(device=self.device, dtype=torch.float32))
            if self.value is None or tuple(self.value.shape) != (1, 1025, 1536):
                raise ValueError('Unexpected qkv value shape')
            patches = torch.nn.functional.normalize(self.value[:, 1:, :], dim=-1)
            if not torch.isfinite(patches).all():
                raise ValueError('Non-finite patches')
            return patches[0].cpu().numpy()

    def close(self):
        self.hook.remove()
