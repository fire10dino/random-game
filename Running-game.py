import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Blue Bob's Tiny Adventure", layout="centered")
st.title("Blue Bob's Tiny Adventure")

# Credits directly after the title
st.markdown("""
**Credits:**  
Created by: **Fire10dino** (player/idea) & **ChatGPT** (code helper)  
Built with: **Streamlit** + **HTML5 Canvas & JavaScript**  
Special thanks to: The **open-source community** behind Streamlit and JS game dev!
""")

st.markdown("""
A tiny 2D endless runner implemented in plain HTML5 canvas + JavaScript embedded into Streamlit.  
Controls:
- Space / Up arrow / Tap = jump
- Click "Restart" button below the game to restart
""")

# Sliders to adjust game parameters
difficulty = st.slider("Difficulty (obstacle spawn speed)", min_value=1.0, max_value=4.0, value=2.0, step=0.1)
height = st.slider("Canvas height (px)", min_value=300, max_value=800, value=420)

HTML = f'''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      html,body {{ margin:0; padding:0; }}
      #game {{ display:block; margin:0 auto; background:#f4f7fb; border:1px solid #ccc; }}
      .overlay {{ font-family: Arial, sans-serif; text-align:center; margin-top:8px; }}
      #restart {{ padding:8px 12px; font-size:14px; }}
    </style>
  </head>
  <body>
    <canvas id="game" width="700" height="{height}"></canvas>
    <div class="overlay">
      <div id="score">Green Score: 0 | Red Score: 0</div>
      <button id="restart">Restart</button>
      <div style="font-size:12px; color:#666; margin-top:6px;">Difficulty: {difficulty}</div>
    </div>

    <script>
    (()=>{{
      const canvas = document.getElementById('game');
      const ctx = canvas.getContext('2d');
      const W = canvas.width; const H = canvas.height;

      // Parameters
      const difficulty = {difficulty};
      const jumpStrength = -16;
      const groundY = H - 30;

      // Game state
      let player = {{ x:80, y:H - 80, w:36, h:48, vy:0, grounded:false }};
      const gravity = 0.9;

      let obstacles = [];
      let spawnTimer = 0;
      let speed = 4 + (difficulty - 1) * 1.5;

      let greenScore = 0;
      let redScore = 0;
      let alive = true;

      function reset(){{
        player.y = groundY - player.h;
        player.vy = 0;
        obstacles = [];
        spawnTimer = 0;
        greenScore = 0;
        redScore = 0;
        alive = true;
        speed = 4 + (difficulty - 1) * 1.5;
        document.getElementById('score').innerText = 'Green Score: 0 | Red Score: 0';
      }}

      function spawnObstacle(){{
        const h = 24 + Math.random()*48;
        const isGreen = Math.random() < (1/7); // 1 in 7 chance for green
        obstacles.push({{ 
          x: W + 20, 
          y: groundY - h, 
          w: 20, 
          h: h, 
          green: isGreen 
        }});
      }}

      function update(){{
        if(!alive) return;

        // player physics
        player.vy += gravity;
        player.y += player.vy;
        if(player.y + player.h >= groundY){{
          player.y = groundY - player.h;
          player.vy = 0;
          player.grounded = true;
        }} else {{
          player.grounded = false;
        }}

        // obstacles
        for(let i = obstacles.length-1; i>=0; --i){{
          const ob = obstacles[i];
          ob.x -= speed;

          if(ob.x + ob.w < -50){{
            // Red block jumped over
            if(!ob.green) redScore++;
            obstacles.splice(i,1);
          }}
        }}

        // spawn
        spawnTimer += 1;
        const spawnInterval = Math.max(40, 120 - difficulty*20);
        if(spawnTimer > spawnInterval){{
          spawnTimer = 0;
          spawnObstacle();
        }}

        // collision check
        for(let i = obstacles.length-1; i>=0; --i){{
          const ob = obstacles[i];
          if(rectIntersect(player.x, player.y, player.w, player.h, ob.x, ob.y, ob.w, ob.h)){{
            if(ob.green){{
              greenScore++;
              obstacles.splice(i,1); // collect green block
            }} else {{
              alive = false; // hit red block = game over
            }}
          }}
        }}

        document.getElementById('score').innerText = 
          'Green Score: ' + greenScore + ' | Red Score: ' + redScore;

        // gradually increase speed
        speed += 0.0007;
      }}

      function rectIntersect(x1,y1,w1,h1,x2,y2,w2,h2){{
        return !(x2 > x1 + w1 || x2 + w2 < x1 || y2 > y1 + h1 || y2 + h2 < y1);
      }}

      function draw(){{
        // background
        ctx.fillStyle = '#f4f7fb';
        ctx.fillRect(0,0,W,H);

        // ground
        ctx.fillStyle = '#e9eef5';
        ctx.fillRect(0, groundY, W, H-groundY);

        // player
        ctx.fillStyle = '#3b82f6';
        ctx.fillRect(player.x, player.y, player.w, player.h);
        ctx.fillStyle = '#fff';
        ctx.fillRect(player.x + player.w - 10, player.y + 10, 6, 6);

        // obstacles
        for(const ob of obstacles){{
          ctx.fillStyle = ob.green ? '#22c55e' : '#ef4444'; // green or red
          ctx.fillRect(ob.x, ob.y, ob.w, ob.h);
        }}

        // game over overlay
        if(!alive){{
          ctx.fillStyle = 'rgba(0,0,0,0.5)';
          ctx.fillRect(0,0,W,H);
          ctx.fillStyle = '#fff';
          ctx.font = '28px Arial';
          ctx.textAlign = 'center';
          ctx.fillText('Game Over', W/2, H/2 - 30);
          ctx.font = '18px Arial';
          ctx.fillText('Green Score: ' + greenScore, W/2, H/2);
          ctx.fillText('Red Score: ' + redScore, W/2, H/2 + 30);
          ctx.fillText('Click Restart or press Space to play again', W/2, H/2 + 60);
        }}
      }}

      async function loop(){{
        while(true){{
          update();
          draw();
          await new Promise(r => requestAnimationFrame(r));
        }}
      }}

      // controls
      window.addEventListener('keydown', (e)=>{{
        if(e.code === 'Space' || e.code === 'ArrowUp'){{
          e.preventDefault();
          if(!alive) reset();
          if(player.grounded) player.vy = jumpStrength;
        }}
      }});

      canvas.addEventListener('pointerdown', ()=>{{
        if(!alive) reset();
        if(player.grounded) player.vy = jumpStrength;
      }});

      document.getElementById('restart').addEventListener('click', ()=>reset());

      reset();
      loop();
    }})();
    </script>
  </body>
</html>
'''

components.html(HTML, height=height+160, scrolling=True)

