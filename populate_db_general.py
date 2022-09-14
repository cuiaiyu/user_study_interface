
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

def load_image_path(images_folder):
    #import pdb; pdb.set_trace()
    files = os.listdir(images_folder)
    files = sorted(files)
    files = [os.path.join(images_folder, file) for file in files]
    return files

def load_all_images(path_dict):
    ret = {}
    for name in path_dict:
        ret[name] = load_image_path(path_dict[name])
    return ret

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
        

    #import pdb; pdb.set_trace()
    peers_dict, pose_ref, viton_ref = load_all_images(peers_dir_dict, unwanted=unwanted_index)
    ours_dict, _, viton_ref = load_all_images(ours_dir_dict, unwanted=unwanted_index)
    # import pdb; pdb.set_trace()
    curr_qid = pop_db(peers_dict, ours_dict, pose_ref, viton_ref, save_dir, viton=True)
    print("%d questions populated." % curr_qid)


