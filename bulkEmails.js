import { CourierClient } from "@trycourier/courier";

const courier = new CourierClient({
  authorizationToken: "",
});

const emails = [];

const sendEmails = async (emails, template) => {
  for (const email of emails) {
    try {
      const { requestId } = await courier.send({
        message: {
          to: {
            email: email,
          },
          // Use your template ID here
          template,
          data: {},
        },
      });
      console.log(`Email sent to ${email}. Request ID: ${requestId}`);
    } catch (error) {
      console.error(
        `Failed to send email to ${email}. Error: ${error.message}`
      );
    }
  }
};

// ns users
// sendEmails(emails, "4ETHQW9EQ34JCAHSW9MPWN5YNAJR");

// pod user
// sendEmails(emails, "7YDNJQEGBJMXRVGWQHC748EPQJ6S");

// auto payment
sendEmails(emails, "GVEWC7XWYEMA6JKKWPKB3DKVA8QT");
