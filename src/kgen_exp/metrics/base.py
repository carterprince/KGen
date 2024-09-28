from concurrent.futures import ProcessPoolExecutor
from PIL import Image
from tqdm import tqdm, trange


pool = ProcessPoolExecutor(max_workers=16)


def load(image):
    if isinstance(image, str):
        return Image.open(image).convert("RGB")
    else:
        return image


def batch_load(images, loading_func=load):
    return list(tqdm(pool.map(loading_func, images), total=len(images), leave=False))


class MetricRunner:
    single = False
    multi = False
    img_load_func = load

    def eval(self, images, ref_texts=None, is_ref=False):
        raise NotImplementedError()

    def eval_single(self, image, ref_text=None, is_ref=False):
        if isinstance(image, (Image.Image, str)):
            image = [image]
        if isinstance(ref_text, str):
            ref_text = [ref_text]
        image = batch_load(image, self.img_load_func)

        return self.eval(image, ref_text, is_ref=is_ref)

    def eval_multi(self, images, ref_texts=None, ref_images=None, batch_size=32):
        if ref_texts is None:
            ref_texts = [None] * max(len(images), len(ref_images))
        results = []
        ref_results = []
        for i in trange(0, len(images), batch_size):
            results.append(
                self.eval_single(
                    images[i : i + batch_size],
                    ref_texts[i : i + batch_size],
                    is_ref=False,
                )
            )
        if ref_images is not None:
            for i in trange(0, len(ref_images), batch_size):
                ref_results.append(
                    self.eval_single(
                        ref_images[i : i + batch_size],
                        ref_texts[i : i + batch_size],
                        is_ref=True,
                    )
                )

        return results, ref_results