console.log("now say my name");

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

$.ajax({
  type: "GET",
  url: "/speciality-json/",
  success: (response) => {
    const specialities = response.data;

    specialities.map((speciality) => {
      // now we want to re-create options for each car and show it
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

  doctorDropDown.innerHTML = "";
  doctorDropDown.textContent = "دکتر خود را انتخاب کنید";

  $.ajax({
    type: "GET",
    url: `doctor-json/${+speciality_id}`,
    success: (response) => {
      doctors = response.data;
      doctors.map((doctor) => {
        // console.log(doctor.id);
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
  console.log(doctor_id);

  // Clear the options from the doctorTime select element
  doctorTime.innerHTML = "";
  doctorTime.textContent = "نوبت های در دسترس";

  $.ajax({
    type: "GET",
    url: `/schedule-json/${+doctor_id}/`,
    success: (response) => {
      const slots = response.data;
      console.log(slots);
      slots?.map((slot) => {
        const option = document.createElement("option");
        option.textContent = `${convertNumToDay(
          slot.day_of_week
        )}: ${slot.time_slots__start_time.substring(
          0,
          slot.time_slots__start_time.lastIndexOf(":")
        )} - ${slot.time_slots__end_time.substring(
          0,
          slot.time_slots__end_time.lastIndexOf(":")
        )}`;
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
  const dayIndex = doctorTime.indexOf(":");
  const day = doctorTime.slice(0, dayIndex);
  const time = doctorTime.slice(dayIndex + 1);
  const firstName = document.querySelector("#first-name").value;
  const lastName = document.querySelector("#last-name").value;
  const phone = document.querySelector("#phone").value;

  $.ajax({
    type: "POST",
    url: "/create/",
    data: {
      csrfmiddlewaretoken: csrf[0].value,
      doctor: doctor,
      day: convertDayToNum(day),
      patient: {
        first_name: firstName,
        last_name: lastName,
        phone: phone,
      },
    },
    success: (response) => {
      const trackingNumber = response.data.tracking_number;
      console.log(`Your tracking number is ${trackingNumber}`);
      // do something with the tracking number, like display it to the user
    },
    error: (error) => console.log(error),
  });
};

document.querySelector("form").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent the form from submitting normally
  createAppointment(); // Call the createAppointment function
});
