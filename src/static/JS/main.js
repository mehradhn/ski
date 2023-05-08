const specialityDropDown = document.getElementById("speciality");
const doctorDropDown = document.getElementById("doctor");
const doctorTime = document.getElementById("doctor-time");
const csrf = document.getElementsByName("csrfmiddlewaretoken");
const days = [
  "شنبه",
  "یکشنبه",
  "دوشنبه",
  "سه شنبه",
  "چهارشنبه",
  "پنجشنبه",
  "جمعه",
];
const convertNumToDay = (num) => days[num];
const convertDayToNum = (day) => days.indexOf(day);

// Default text for speciality dropdown
const currentUrl = window.location.href;

if (currentUrl.includes("track-number")) {
  const result_track = document.getElementById("result-track");
  const btn = document.getElementById("search-btn");
  btn.addEventListener("click", () => {
    const tracking_number_client = document.querySelector(
      "#track-number-client"
    ).value;
    console.log(tracking_number_client);
    $.ajax({
      type: "GET",
      url: "/appointment-data/",
      data: {
        tracking_number: tracking_number_client,
      },
      success: (response) => {
        if (response.data) {
          result_track.textContent = `نوبت شما در روز  ${response.data.day}  در ساعت  ${response.data.time_slot} با  ${response.data.doctor}  ثبت شده است `;
        } else {
          result_track.textContent = `چنین نوبتی در دیتابیس ذخیره نشده است در صورت خطا با پشتیبانی تماس بگیرید`;
        }
      },
      error: (error) => alert("لطفا فقط عدد وارد کنید"),
    });
  });
  const trackNumberClient = document.getElementById("track-number-client");
} else {
  const defaultSpecialityOption = document.createElement("option");
  defaultSpecialityOption.textContent = "تخصص";
  defaultSpecialityOption.setAttribute("value", "");
  defaultSpecialityOption.setAttribute("disabled", "");
  defaultSpecialityOption.setAttribute("selected", "");
  specialityDropDown.appendChild(defaultSpecialityOption);

  $.ajax({
    type: "GET",
    url: "/speciality-json/",
    success: (response) => {
      const specialities = response.data;
      specialities.map((speciality) => {
        const option = document.createElement("option");
        option.textContent = speciality.name;
        option.setAttribute("value", speciality.id);
        specialityDropDown.appendChild(option);
      });
    },
    error: (error) => console.log(error),
  });

  specialityDropDown.addEventListener("change", (e) => {
    const speciality_id = e.target.value;

    // Clear the options from the doctor dropdown
    doctorDropDown.innerHTML = "";
    // Default text for doctor dropdown
    const defaultDoctorOption = document.createElement("option");
    defaultDoctorOption.textContent = "دکتر خود را انتخاب کنید";
    defaultDoctorOption.setAttribute("value", "");
    defaultDoctorOption.setAttribute("disabled", "");
    defaultDoctorOption.setAttribute("selected", "");
    doctorDropDown.appendChild(defaultDoctorOption);

    $.ajax({
      type: "GET",
      url: `doctor-json/${+speciality_id}`,
      success: (response) => {
        doctors = response.data;
        doctors.map((doctor) => {
          const option = document.createElement("option");
          option.textContent = `${doctor.first_name} ${doctor.last_name}`;
          option.setAttribute("value", doctor.id);
          doctorDropDown.appendChild(option);
        });
      },
      error: (error) => console.log(error),
    });
  });

  doctorDropDown.addEventListener("change", (e) => {
    const doctor_id = e.target.value;
    // console.log(doctor_id);

    // Clear the options from the doctorTime select element
    doctorTime.innerHTML = "";

    // Default text for doctorTime dropdown
    const defaultTimeOption = document.createElement("option");
    defaultTimeOption.textContent = "نوبت های در دسترس";
    defaultTimeOption.setAttribute("value", "");
    defaultTimeOption.setAttribute("disabled", "");
    defaultTimeOption.setAttribute("selected", "");
    doctorTime.appendChild(defaultTimeOption);

    $.ajax({
      type: "GET",
      url: `/schedule-json/${+doctor_id}/`,
      success: (response) => {
        const schedules = JSON.parse(response.data);
        // console.log(schedules)
        schedules?.map((schedule) => {
          if (schedule.time_slots[0].is_booked) return;
          const option = document.createElement("option");
          option.textContent = `${convertNumToDay(schedule.day_of_week)}: ${
            schedule.time_slots[0].start_time
          } - ${schedule.time_slots[0].end_time}`;
          option.setAttribute("value", option.textContent);
          doctorTime.appendChild(option);
        });
      },
      error: (error) => console.log(error),
    });
  });

  const createAppointment = () => {
    const speciality = document.querySelector("#speciality").value;
    const doctor = document.querySelector("#doctor").value;
    const doctorTime = document.querySelector("#doctor-time").value;
    const day = convertDayToNum(doctorTime.split(": ")[0]);
    const timeParts = doctorTime.split(" - ");
    const startTime = timeParts[0].split(": ")[1];
    const endTime = timeParts[1];
    const firstName = document.querySelector("#first-name").value;
    const lastName = document.querySelector("#last-name").value;
    const phone = document.querySelector("#phone").value;

    const specificTime = { start_time: startTime, end_time: endTime };
    if (
      !speciality ||
      !doctor ||
      !doctorTime ||
      !firstName ||
      !lastName ||
      !phone
    )
      return alert("لطفا همه فیلد هارو پر کنید");
    $.ajax({
      type: "GET",
      url: "/time-slots-json/",
      success: (response) => {
        const time_slot = response.data.filter(
          (slot) =>
            slot.start_time.substring(0, 5) === specificTime.start_time ||
            slot.end_time.substring(0, 5) === specificTime.end_time
        );
        const time_slot_id = time_slot[0].id;
        $.ajax({
          type: "POST",
          url: "/create/",
          data: {
            csrfmiddlewaretoken: csrf[0].value,
            doctor: doctor,
            day: +day,
            time_slot: +time_slot_id,
            patient: {
              first_name: firstName,
              last_name: lastName,
              phone_number: phone,
            },
          },
          success: (response) => {
            const trackingNumber = response.data.tracking_number;
            alert(`کد رهگیری شما ${trackingNumber}`);
            // do something with the tracking number, like display it to the user
            document.querySelector("#speciality").value = "";
            document.querySelector("#doctor").value = "";
            document.querySelector("#doctor-time").value = "";
            document.querySelector("#first-name").value = "";
            document.querySelector("#last-name").value = "";
            document.querySelector("#phone").value = "";
          },
          error: (error) => console.log(error),
        });
      },
      error: (error) => console.log(error),
    });
  };

  document.querySelector("form").addEventListener("submit", (event) => {
    event.preventDefault(); // Prevent the form from submitting normally
    createAppointment(); // Call the createAppointment function
  });
}
