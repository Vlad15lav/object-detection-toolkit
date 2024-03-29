import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def get_whr(bboxs, labels, xyxy=True, scale=1):
    label_array, height, width = np.zeros(0), np.zeros(0), np.zeros(0)
    ratio, bbox_array = np.zeros(0), np.zeros(0)
    
    for i in range(len(bboxs)):
        bbox = np.array(bboxs[i])
        
        if xyxy:
            w = bbox[:, 2] - bbox[:, 0]
            h = bbox[:, 3] - bbox[:, 1]
        else:
            w, h = bbox[:, 2], bbox[:, 3]
                
        label_array = np.append(label_array, labels[i])
        width = np.append(width, w * scale)
        height = np.append(height, h * scale)
        ratio = np.append(ratio, h / w)
    
    return label_array, width, height, ratio

def analysis_target(label_array, width, height, ratio, category=[32, 96, 128, 256], figs=16):
    label_un = np.sort(np.unique(label_array))
    
    targets = {key:[] for key in label_un}
    rations = {key:[] for key in label_un}
    
    categories = {"<{}*{}".format(key, key):0 for key in category}
    categories['large'] = 0
    keys_cat = list(categories)
    
    for i, gt_cls in enumerate(label_array):
        if width[i] < 5 or height[i] < 5:
            continue
        
        targets[gt_cls].append(width[i])
        targets[gt_cls].append(height[i])
        rations[gt_cls].append(ratio[i])
        
        area = width[i] * height[i]
        for i_key, id_c in enumerate(category):
            if area < id_c * id_c:
                categories[keys_cat[i_key]] += 1
                break
        
    categories['large'] = len(label_array) - sum(categories.values())
    
    # Create DataFrame and Boxplots, Bar by classes
    df_wh = pd.DataFrame(dict([ (k, pd.Series(v)) for k, v in targets.items() ]))
    df_ratio = pd.DataFrame(dict([ (k, pd.Series(v)) for k, v in rations.items() ]))
    df_categories = pd.DataFrame(dict([ (k, pd.Series(v)) for k, v in categories.items() ]))
    
    f, ax = plt.subplots(2, 2, figsize=(figs, figs))
    sns.boxplot(data=df_wh, orient="h", showfliers=False, ax=ax[0, 0]).set_title('Bounding box sizable by classes')
    sns.boxplot(data=df_ratio, orient="h", showfliers=False, ax=ax[0, 1]).set_title('Bounding box ratio by classes')
    sns.barplot(x=[len(v)/2 for k,v in targets.items()], y=df_wh.keys(), orient="h", ax=ax[1, 0]).set_title('Number of boxes by classes')
    sns.barplot(data=df_categories, orient="h", ax=ax[1, 1]).set_title('Bounding box categories')
    plt.show()

def decomposit_boxes(bboxs, anchor_base_scale = 4, anchor_stride = 8):
    return_scale, return_ratio = [], []
    base_factor = anchor_base_scale * anchor_stride
    for height, width in bboxs:
        return_scale.append(height * 1.0 / base_factor)
        return_ratio.append((1, width * 1.0 / height))
    return return_scale, return_ratio
