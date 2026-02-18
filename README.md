               Flow Chart
ผู้ใช้ถาม
   ↓
steering agent เลือก agent ให้
   ↓
investigation_team คิดพร้อมกัน
   - admirer หา info
   - critic ปรับ state
   ↓
judge ตรวจว่าดีพอหรือยัง
   ↓
(ถ้าไม่พอ วนใหม่)
   ↓
verdict_writer สรุปผลลัพธ์

<img width="1305" height="573" alt="image" src="https://github.com/user-attachments/assets/429a85ec-a668-4166-abd5-2cf964f87b0f" />
เริ่มจาก inquiry_agent รับคำถามผู้ใช้ แล้วส่งเข้า investigation_team ให้ admirer หาข้อมูลและ critic ปรับ state ไปพร้อมกัน จากนั้น judge ตัดสินว่างานดีพอหรือยัง ถ้ายังจะวนคิดใหม่ แต่ถ้าพอแล้ว verdict_writer จะสรุปผลลัพธ์และเขียนออกไฟล์ เป็นกระบวนการคิด-ปรับ-ตรวจ-สรุปอย่างเป็นระบบ
<img width="1291" height="560" alt="image" src="https://github.com/user-attachments/assets/8cce745d-3f49-4296-93f9-3377ce2ca809" />
ระบบเริ่มจาก pipeline หลักแบบลำดับขั้น (Sequential) แล้วส่งงานเข้า investigation_team ที่ทำงานพร้อมกันสองบทบาท คือ admirer ไปค้นข้อมูลจาก Wikipedia และ critic นำผลมาปรับ state จากนั้นข้อมูลจะถูกส่งเข้า trial_loop ให้ judge ตรวจว่าดีพอหรือยัง ถ้ายังจะวนคิดใหม่ แต่ถ้าพร้อมแล้วจึงส่งต่อให้ verdict_writer สรุปผลและเขียนออกไฟล์ เป็นกระบวนการคิด-ปรับ-ตรวจ-สรุปอย่างต่อเนื่อง
<img width="1295" height="566" alt="image" src="https://github.com/user-attachments/assets/31206279-f2d7-4e63-9154-e63e78525fa7" />
รับข้อมูลจากการค้นคว้าของ admirer แล้วนำมาวิเคราะห์ ปรับปรุง และอัปเดตลงใน state กลางของระบบ (replace_state) เพื่อให้ข้อมูลดีขึ้นก่อนส่งต่อเข้า trial_loop ให้ judge ตรวจคุณภาพอีกครั้ง เป็นขั้นตอน “ขัดเกลาเนื้อหา” ของทั้งระบบ
<img width="1292" height="567" alt="image" src="https://github.com/user-attachments/assets/90630254-c5ec-49f9-8a27-1de05690781a" />
judge ทำหน้าที่ตัดสินใจใน trial_loop โดยตรวจสอบว่าข้อมูลจากทีมคิดพร้อมกันดีพอหรือยัง หากผ่านเกณฑ์จะสั่ง exit_loop เพื่อหยุดการวนซ้ำและส่งงานไปขั้นสรุปผล แต่ถ้ายังไม่ดีพอ ระบบจะกลับไปให้ admirer และ critic ปรับปรุงใหม่อีกครั้ง เป็นจุดควบคุมคุณภาพของทั้ง pipeline
<img width="1293" height="577" alt="image" src="https://github.com/user-attachments/assets/757a3092-1963-4fb5-966d-05b53b53c43a" />
เมื่อข้อมูลผ่านการคิดและตรวจสอบครบแล้ว verdict_writer จะนำผลลัพธ์ทั้งหมดมาสรุป และส่งไปที่ write_file เพื่อบันทึกเป็น output จริง เป็นจุดที่เปลี่ยน “กระบวนการคิดของหลาย agent” ให้กลายเป็นผลงานที่ใช้งานได้จริง
