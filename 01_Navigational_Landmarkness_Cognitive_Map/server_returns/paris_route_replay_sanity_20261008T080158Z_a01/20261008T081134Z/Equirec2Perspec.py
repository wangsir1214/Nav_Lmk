'''
原址项目中有相关函数：
PrepareXYZPointCloud
可以查阅
'''


import os
import sys
import cv2
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='GSV pano projection')
parser.add_argument('path', metavar= 'PATH', help='pano file')

def xyz2lonlat(xyz):
    atan2 = np.arctan2
    asin = np.arcsin

    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    xyz_norm = xyz / norm
    x = xyz_norm[..., 0:1]
    y = xyz_norm[..., 1:2]
    z = xyz_norm[..., 2:]

    lon = atan2(x, z)
    lat = asin(y)
    lst = [lon, lat]

    out = np.concatenate(lst, axis=-1)
    return out

def lonlat2XY(lonlat, shape):
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    lst = [X, Y]
    out = np.concatenate(lst, axis=-1)

    return out 

class Equirectangular:
    def __init__(self, img_name):
        self._img = cv2.imread(img_name, cv2.IMREAD_COLOR)
        [self._height, self._width, _] = self._img.shape
        #cp = self._img.copy()  
        #w = self._width
        #self._img[:, :w/8, :] = cp[:, 7*w/8:, :]
        #self._img[:, w/8:, :] = cp[:, :7*w/8, :]

    def GetPerspective(self, FOV, THETA, PHI, height, width):
        #
        # THETA is left/right angle, PHI is up/down angle, both in degree
        #

        f = 0.5 * width * 1 / np.tan(0.5 * FOV / 180.0 * np.pi)
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        K = np.array([
                [f, 0, cx],
                [0, f, cy],
                [0, 0,  1],
            ], np.float32)
        K_inv = np.linalg.inv(K)
        
        x = np.arange(width)
        y = np.arange(height)
        x, y = np.meshgrid(x, y)
        z = np.ones_like(x)
        xyz = np.concatenate([x[..., None], y[..., None], z[..., None]], axis=-1)
        xyz = xyz @ K_inv.T

        y_axis = np.array([0.0, 1.0, 0.0], np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], np.float32)
        # print("in GetPerspective: THETA: ", THETA)
        R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
        R = R2 @ R1
        xyz = xyz @ R.T
        lonlat = xyz2lonlat(xyz) 
        XY = lonlat2XY(lonlat, shape=self._img.shape).astype(np.float32)
        persp = cv2.remap(self._img, XY[..., 0], XY[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)

        return persp
    

if __name__ == '__main__':
    # 测试样例：
    args = parser.parse_args()
    print( 'image from:', args.path )
    equ = Equirectangular(args.path)    # Load equirectangular image

    #/home/jiafurong/data/WallPano/zzKv8yMT2FEVJjLTSifL7w.jpg
    # FOV unit is degree 
    # theta is z-axis angle(right direction is positive, left direction is negative)import sys

    # phi is y-axis angle(up direction positive, down direction negative)
    # height and width is output image dimension 

    # img = equ.GetPerspective(60, 0, 0, 720, 1080) # Specify parameters(FOV, theta, phi, height, width)
    for theta in [-179, -135, -90, -45, 0, 45, 90, 135, 179]:
        img = equ.GetPerspective(90, theta, 0, 512, 512)
        print(img)
        import numpy as np
        img_array=np.array(img)
        print(img_array.shape)

        img_array = np.transpose(img_array, (2, 0, 1))
        print(img_array.shape)
        cv2.imwrite('test2_E2P_theta_%d.jpg' % theta, img)
    # cv2.imwrite('test_E2P.jpg', img)
