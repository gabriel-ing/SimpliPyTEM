
import cv2 as cv
import numpy as np 

def find_shift(frame1, frame2, crop=3700):
    if len(frame1.shape)==3:
        #print(frame1, frame2)
        frame1=np.sum(frame1, axis=0)
        #print(frame1.shape)
    frame1[frame1>frame1.mean()+4*frame1.std()]=frame1.mean()
    frame2[frame2>frame1.mean()+4*frame1.std()] = frame2.mean()
    frame1_cropped = frame1[:crop, :crop]
    frame2_cropped = frame2[:crop, :crop]
    
    #frame1_cropped =cv.resize(frame1_cropped, (int(frame1_cropped.shape[0]/2), int(frame1_cropped.shape[1]/2)), interpolation=cv.INTER_CUBIC)
    #frame2_cropped =cv.resize(frame2_cropped, (int(frame2_cropped.shape[0]/2), int(frame2_cropped.shape[1]/2)), interpolation=cv.INTER_CUBIC)
    center = (int(frame1_cropped.shape[0]/2), int( frame1_cropped.shape[1]/2))
    
    #mask = np.zeros_like(frame1_cropped)
    #mask= cv.circle(mask,center, LP_radius*2,1,-1)
    
    fft1 = cv.dft(frame1_cropped.astype(np.float32), flags=cv.DFT_COMPLEX_OUTPUT)
    fft2 = cv.dft(frame2_cropped.astype(np.float32), flags=cv.DFT_COMPLEX_OUTPUT)
    fft1_shf = np.fft.fftshift(fft1)
    fft2_shf = np.fft.fftshift(fft2)
    
    #mask = np.zeros_like(fft1)
    #mask= cv.circle(mask,center, LP_radius*2,1,-1)
    #print(fft1_shf.shape)
    #fft1_filtered = mask*fft1_shf
    #fft2_filtered = mask*fft2_shf
    
    
    fft1_shf_cplx = fft1_shf[:,:,0]+1j*fft1_shf[:,:,1]
    fft2_shf_cplx = fft2_shf[:,:,0]+1j*fft2_shf[:,:,1]

    
    fft1_shf_abs = np.abs(fft1_shf_cplx)
    fft2_shf_abs = np.abs(fft2_shf_cplx)
    total_abs = fft1_shf_abs*fft2_shf_abs
    
    p_real = (np.real(fft1_shf_cplx)*np.real(fft2_shf_cplx)+np.imag(fft1_shf_cplx)*np.imag(fft2_shf_cplx))/total_abs
    p_imag = (np.imag(fft1_shf_cplx)*np.real(fft2_shf_cplx)+np.real(fft1_shf_cplx)*np.imag(fft2_shf_cplx))/total_abs
    p_complex = p_real + 1j*p_imag
    p_inverse = np.abs(np.fft.ifft2(p_complex))
    #print(p_inverse)
    max_val = np.max(p_inverse)
    #print(max_val)
    
    shifts = np.where(p_inverse==max_val)
    print(shifts)
    shift_x = shifts[0][0]
    shift_y = shifts[1][0]
    if shift_x==0:
        p_inverse[shift_x, shift_y]=0
        print('shift=0')
        shifts=np.where(p_inverse==np.max(p_inverse))
        print(shifts)
        shift_x = shifts[0][0]
        shift_y = shifts[1][0]
    return shift_x, shift_y

def shift_elements(arr, shifts, fill_value):
    result = np.empty_like(arr)
    x = shifts[0]
    if x>0:
        result[:x]=fill_value
        result[x:] = arr[:-x]
    elif x<0: 
        result[x]=fill_value
        result[:x]=arr[-x:]
    else:
        result =arr
    #print(result)   
    r2 = np.zeros_like(result)
    #print(r2)
    y = shifts[1]
    #print(y)
    if y>0:
        r2[:,:y]=fill_value
        r2[:,y:]=result[:,:-y]
    elif y<0:
        r2[:,y] = fill_value
        r2[:, :y]=result[:, -y:] 
    else:
        r2=result
    #print(result)
    return r2    
