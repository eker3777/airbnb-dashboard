def test_animation_speed():
    import streamlit as st
    import time

    st.title('Animation Speed Test')

    animation_speed = 0.1  # Adjust this value to change the speed of the animation

    for i in range(10):
        st.write(f'Frame {i}')
        time.sleep(animation_speed)