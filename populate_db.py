
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gui.settings")
import django
django.setup()
from FEdit.models import Question, Choice

import random
import numpy as np
import imageio
from tqdm import tqdm
import cv2

MAX = 700

def load_standard_images(images_folder, indices=[],unwanted=[]):
    #import pdb; pdb.set_trace()
    input_images = []
    generated_images = []
    names = []
    count = 0
    files = os.listdir(images_folder)
    files = sorted(files)
    if not indices:
        indices = range(len(files))
    for index in tqdm(indices, "loading from %s" % images_folder):
        img_name = "generated_%d.jpg" % (index + 1)
        if index + 1 in unwanted:
            continue
        img = imageio.imread(os.path.join(images_folder, img_name))
        # print(os.path.join(images_folder, img_name))
        if count > MAX:
           break
        count += 1
        if img.shape[1] % 3 == 0:
            img = cv2.resize(img, (176*3, 256))
            w = int(img.shape[1] / 3) #h, w ,c
            input_images.append(img[:, :2*w])
            generated_images.append(img[:, 2*w:3*w])
        else:
            w = int(img.shape[1] / 5)
            ref_img = np.concatenate([img[:, :w], img[:, 2*w:3*w]], 1)
            input_images.append(ref_img)
            generated_images.append(img[:, 4*w:])
    return input_images, generated_images


def load_all_images(path_dict, indices=[],unwanted=[]):
    ret_dict = dict()
    pose_ref = []
    viton_ref = []
    for exp in path_dict:
        folder = path_dict[exp]
        if 'adgan' in exp:
            pose_ref, ret_dict[exp] = load_standard_images(folder, indices,unwanted)
        else:
            viton_ref, ret_dict[exp] = load_standard_images(folder, indices,unwanted)
    return ret_dict, pose_ref, viton_ref


def pop_db(ref_dict, our_dict, pose_ref, viton_ref, save_dir, start_qid=0, viton=True):

    if not viton:
        prefix = "posetrans"
        q_text = "Given a target person (left) and a target pose (right), \
        which one of the two generated images looks more like the same person in the targeted pose?"
        refs = pose_ref
    else:
        prefix = "viton"
        q_text = "Given a target person (left) and a target upper-clothes (right), \
        which one of the two generated images looks more like the given person wearing the given upper-clothes?"
        refs = viton_ref
    qid = start_qid
    for base_name,ours_name in zip(ref_dict, ours_dict):
        # import pdb; pdb.set_trace()
        for i, (ref, base, our) in tqdm(enumerate(zip(refs, ref_dict[base_name], our_dict[ours_name]))):
            qid += 1
            save_question(ref, base, our, base_name, ours_name, q_text, prefix, qid, save_dir)
            if i >= MAX:
                break
    return qid


def save_question(ref_img, A_img, B_img, A_note, B_note, q_text, prefix, qid, save_dir):
    # save images
    # set questions
    q_fn = "%s_q%d_ref.png" % (prefix, qid)
    a1_fn = "%s_q%d_a1.png" % (prefix, qid)
    a2_fn = "%s_q%d_a2.png" % (prefix, qid)

    imageio.imwrite(os.path.join('static', save_dir, q_fn), ref_img)
    q = Question(
        question_text=q_text,
        question_ref_image= save_dir + '/' + q_fn,
        question_type='conditional real/fake',
        question_cata=prefix,
    )
    q.save()
    note_prefix = "%s vs. %s; " % (A_note, B_note)
    if random.random() > 0.5: 
        imageio.imwrite(os.path.join('static', save_dir, a1_fn), A_img)
        imageio.imwrite(os.path.join('static', save_dir, a2_fn), B_img)

        q.choice_set.create(choice_text='A', query_image=os.path.join(save_dir, a1_fn), notes=note_prefix + A_note, votes=0)
        q.choice_set.create(choice_text='B', query_image=os.path.join(save_dir, a2_fn), notes=note_prefix + B_note, votes=0)
    else:
        imageio.imwrite(os.path.join('static', save_dir, a1_fn), B_img)
        imageio.imwrite(os.path.join('static', save_dir, a2_fn), A_img)

        q.choice_set.create(choice_text='A', query_image=os.path.join(save_dir, a1_fn), notes=note_prefix + B_note, votes=0)
        q.choice_set.create(choice_text='B', query_image=os.path.join(save_dir, a2_fn), notes=note_prefix + A_note, votes=0)

    # q.choice_set.create(choice_text='Both Unrecognizable', notes=note_prefix + 'fail', votes=0)
    q.save()


if __name__ == '__main__':
    
    root = '/shared/rsaas/aiyucui2/inshop/checkpoints/'
    if True:
        with open("pose_random_index.txt", "r") as f:
            indices = f.readline()
            indices = indices.split(",")
            indices = [int(i) for i in indices]
        save_dir = "pose"
        if not os.path.exists('static/%s' % save_dir):
            os.mkdir('static/%s' % save_dir)

        # ADGAN vs ours
        peers_dir_dict = {
            'adgan':root + "yifang_800",
            'gfla': root + "eval_results_256jpg/fashion",
        }
        ours_dir_dict = {
            "ours-176":root + "adseq2_vgg_large1_latest_jpg",
            "ours-256": root + "adseq2_vgg_large_square_latest_jpg",
            }
        peers_dict, pose_ref, viton_ref = load_all_images(peers_dir_dict, indices)
        ours_dict, _, _ = load_all_images(ours_dir_dict, indices)
        curr_qid = pop_db(peers_dict, ours_dict, pose_ref, viton_ref, save_dir, viton=False)
        print("%d questions populated." % curr_qid)

    peers_dir_dict = {'adgan':root + "viton_yifang_1000",}
    ours_dir_dict = { "ours":root + "viton_adseq2_vgg_large1_latest",}
    save_dir = "viton"
    
    if not os.path.exists('static/%s' % save_dir):
        os.mkdir('static/%s' % save_dir)
        
    unwanted_index = [
        1,7,15,16,21,26,27,49,52,54,64,78,87,96,
        108,123,163,175,181,186,
        202,203,204,206,229,234,260,264,268,276,277,279,290,295,
        303,305,314,315,319,336,344,345,347,353,356,357,358,359,364,368,373,377,395,
        403,406,412,429,453,460,463,466,472,476,497,498,
        506,513,515,517,530,538,548,551,557,573,579,580,590,599,
        601,604,609,611,613,614,617,618,625,626,628,636,637,645,657,659,665,683,686,689,690,696
    ]
    #unwanted_index = [i-1 for i in unwanted_index]
    #import pdb; pdb.set_trace()
    peers_dict, pose_ref, viton_ref = load_all_images(peers_dir_dict, unwanted=unwanted_index)
    ours_dict, _, viton_ref = load_all_images(ours_dir_dict, unwanted=unwanted_index)
    # import pdb; pdb.set_trace()
    curr_qid = pop_db(peers_dict, ours_dict, pose_ref, viton_ref, save_dir, viton=True)
    print("%d questions populated." % curr_qid)


